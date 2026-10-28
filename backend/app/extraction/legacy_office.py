from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from threading import BoundedSemaphore, Event, Timer
from uuid import uuid4

from .base import DocumentChunk, DocumentProcessingError
from .office import extract_docx_chunks, extract_pptx_chunks


MAX_LEGACY_FILE_BYTES = 50 * 1024 * 1024
CONVERSION_TIMEOUT_SECONDS = 60
OLE_COMPOUND_FILE_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")
LEGACY_CONVERSION_OPT_IN = "ARCHIBOT_ENABLE_LEGACY_OFFICE_CONVERSION"
_conversion_slot = BoundedSemaphore(1)


def _read_conversion(binary: str, container_name: str) -> bytes:
    timed_out = Event()
    with subprocess.Popen(
        [binary, "start", "--attach", container_name],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    ) as process:
        def terminate() -> None:
            timed_out.set()
            process.kill()

        timer = Timer(CONVERSION_TIMEOUT_SECONDS, terminate)
        timer.start()
        try:
            if process.stdout is None:
                raise DocumentProcessingError("The Office converter output is unavailable.")
            converted = process.stdout.read(MAX_LEGACY_FILE_BYTES + 1)
            if len(converted) > MAX_LEGACY_FILE_BYTES:
                process.kill()
                raise DocumentProcessingError("The converted Office document exceeds 50 MB.")
            process.wait()
            if timed_out.is_set():
                raise DocumentProcessingError("Legacy Office conversion exceeded the 60-second limit.")
            if process.returncode != 0 or not converted:
                raise DocumentProcessingError("LibreOffice could not convert this legacy Office document.")
            return converted
        finally:
            timer.cancel()
            timer.join()
            if process.poll() is None:
                process.kill()


def _convert_legacy_office(data: bytes, extension: str) -> bytes:
    if not data or len(data) > MAX_LEGACY_FILE_BYTES:
        raise DocumentProcessingError("The legacy Office document is empty or exceeds 50 MB.")
    if not data.startswith(OLE_COMPOUND_FILE_SIGNATURE):
        raise DocumentProcessingError("The legacy Office document is invalid.")
    if os.environ.get(LEGACY_CONVERSION_OPT_IN, "").lower() != "true":
        raise DocumentProcessingError(
            "Legacy Office conversion is disabled until an isolated converter is configured."
        )

    image = os.environ.get("ARCHIBOT_LEGACY_OFFICE_IMAGE", "")
    if not image or image.startswith("-") or any(character.isspace() for character in image):
        raise DocumentProcessingError("An isolated LibreOffice container image must be configured.")
    binary = shutil.which("docker")
    if not binary:
        raise DocumentProcessingError("Legacy DOC/PPT conversion requires Docker on the server.")
    if not _conversion_slot.acquire(blocking=False):
        raise DocumentProcessingError("Legacy Office conversion is busy. Retry later.")

    try:
        with TemporaryDirectory(prefix="archibot-office-") as temporary_directory:
            work_dir = Path(temporary_directory)
            input_dir = work_dir / "input"
            input_dir.mkdir()
            input_path = input_dir / f"source.{extension}"
            input_path.write_bytes(data)
            if os.name == "posix":
                input_dir.chmod(0o755)
                input_path.chmod(0o444)
            container_name = f"archibot-office-{uuid4().hex}"
            try:
                subprocess.run(
                    [
                        binary, "create", "--name", container_name, "--pull", "never",
                        "--network", "none", "--read-only", "--user", "65534:65534",
                        "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true",
                        "--cpus", "1", "--memory", "512m", "--memory-swap", "512m",
                        "--pids-limit", "64", "--ulimit", "fsize=52428800:52428800",
                        "--log-driver", "none", "--init",
                        "--mount", f"type=bind,source={input_dir},target=/input,readonly",
                        "--tmpfs", "/work:rw,noexec,nosuid,nodev,size=134217728,uid=65534,gid=65534,mode=700",
                        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=67108864,mode=1777",
                        "--env", "HOME=/work", "--entrypoint", "/usr/bin/timeout",
                        image, "--signal=TERM", "--kill-after=5s", "50s",
                        "/usr/bin/python3", "/opt/archibot/convert.py", extension,
                    ],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
                )
                converted = _read_conversion(binary, container_name)
                state = subprocess.run(
                    [binary, "inspect", "--format", "{{.State.ExitCode}}", container_name],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=15,
                )
                if state.stdout.strip() != b"0":
                    raise DocumentProcessingError("LibreOffice could not convert this legacy Office document.")
                return converted
            finally:
                subprocess.run(
                    [binary, "rm", "--force", container_name],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
                )
    except DocumentProcessingError:
        raise
    except subprocess.TimeoutExpired as exc:
        raise DocumentProcessingError("Legacy Office conversion exceeded the 60-second limit.") from exc
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DocumentProcessingError("The isolated Office converter failed. Check its Docker configuration.") from exc
    finally:
        _conversion_slot.release()


def extract_doc_chunks(data: bytes, **chunk_options: int) -> list[DocumentChunk]:
    return extract_docx_chunks(_convert_legacy_office(data, "doc"), **chunk_options)


def extract_ppt_chunks(data: bytes, **chunk_options: int) -> list[DocumentChunk]:
    return extract_pptx_chunks(_convert_legacy_office(data, "ppt"), **chunk_options)