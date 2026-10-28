from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from .base import DocumentChunk, DocumentProcessingError
from .office import extract_docx_chunks, extract_pptx_chunks


MAX_LEGACY_FILE_BYTES = 50 * 1024 * 1024
CONVERSION_TIMEOUT_SECONDS = 60
OLE_COMPOUND_FILE_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")
LEGACY_CONVERSION_OPT_IN = "ARCHIBOT_ENABLE_LEGACY_OFFICE_CONVERSION"


def _convert_legacy_office(data: bytes, extension: str, target_format: str) -> bytes:
    if not data or len(data) > MAX_LEGACY_FILE_BYTES:
        raise DocumentProcessingError("The legacy Office document is empty or exceeds 50 MB.")
    if not data.startswith(OLE_COMPOUND_FILE_SIGNATURE):
        raise DocumentProcessingError("The legacy Office document is invalid.")
    if os.environ.get(LEGACY_CONVERSION_OPT_IN, "").lower() != "true":
        raise DocumentProcessingError(
            "Legacy Office conversion is disabled until an isolated converter is configured."
        )

    binary = os.environ.get("LIBREOFFICE_BINARY") or shutil.which("soffice") or shutil.which("libreoffice")
    if not binary:
        raise DocumentProcessingError("Legacy DOC/PPT conversion requires LibreOffice on the server.")

    try:
        with TemporaryDirectory(prefix="archibot-office-") as temporary_directory:
            work_dir = Path(temporary_directory)
            input_path = work_dir / f"source.{extension}"
            output_dir = work_dir / "converted"
            profile_dir = work_dir / "profile"
            output_dir.mkdir()
            input_path.write_bytes(data)
            completed = subprocess.run(
                [
                    binary,
                    f"-env:UserInstallation={profile_dir.as_uri()}",
                    "--headless",
                    "--norestore",
                    "--nodefault",
                    "--nolockcheck",
                    "--nofirststartwizard",
                    "--convert-to",
                    target_format,
                    "--outdir",
                    str(output_dir),
                    str(input_path),
                ],
                check=False,
                capture_output=True,
                timeout=CONVERSION_TIMEOUT_SECONDS,
            )
            output_path = output_dir / f"source.{target_format}"
            if completed.returncode != 0 or not output_path.is_file():
                raise DocumentProcessingError("LibreOffice could not convert this legacy Office document.")
            if not 0 < output_path.stat().st_size <= MAX_LEGACY_FILE_BYTES:
                raise DocumentProcessingError("The converted Office document is empty or exceeds 50 MB.")
            converted = output_path.read_bytes()
            return converted
    except DocumentProcessingError:
        raise
    except subprocess.TimeoutExpired as exc:
        raise DocumentProcessingError("Legacy Office conversion exceeded the 60-second limit.") from exc
    except OSError as exc:
        raise DocumentProcessingError("LibreOffice could not read or convert this document.") from exc


def extract_doc_chunks(data: bytes, **chunk_options: int) -> list[DocumentChunk]:
    return extract_docx_chunks(_convert_legacy_office(data, "doc", "docx"), **chunk_options)


def extract_ppt_chunks(data: bytes, **chunk_options: int) -> list[DocumentChunk]:
    return extract_pptx_chunks(_convert_legacy_office(data, "ppt", "pptx"), **chunk_options)