from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


MAX_OUTPUT_BYTES = 50 * 1024 * 1024


def convert(extension: str) -> None:
    target_format = {"doc": "docx", "ppt": "pptx"}[extension]
    subprocess.run(
        [
            "/usr/bin/libreoffice", "-env:UserInstallation=file:///work/profile",
            "--headless", "--norestore", "--nodefault", "--nofirststartwizard",
            "--convert-to", target_format, "--outdir", "/work", f"/input/source.{extension}",
        ],
        check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, timeout=45,
    )
    output = Path(f"/work/source.{target_format}")
    if output.is_symlink() or not output.is_file() or not 0 < output.stat().st_size <= MAX_OUTPUT_BYTES:
        raise ValueError("Invalid conversion output")
    with output.open("rb") as converted:
        shutil.copyfileobj(converted, sys.stdout.buffer)


if __name__ == "__main__":
    convert(sys.argv[1])