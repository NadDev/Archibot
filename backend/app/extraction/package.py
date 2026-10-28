from __future__ import annotations

from io import BytesIO
from zipfile import BadZipFile, ZipFile

from .base import DocumentProcessingError


MAX_ARCHIVE_ENTRIES = 2_000
MAX_ARCHIVE_MEMBER_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_EXPANSION_RATIO = 200


def validate_office_archive(data: bytes, required_member: str) -> None:
    try:
        with ZipFile(BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_ENTRIES:
                raise DocumentProcessingError("The document contains too many archive entries.")
            total_uncompressed = 0
            names = set()
            for member in members:
                name = member.filename
                if "\\" in name or name.startswith("/") or ".." in name.split("/"):
                    raise DocumentProcessingError("The document contains an unsafe archive path.")
                if member.flag_bits & 1:
                    raise DocumentProcessingError("Encrypted document packages are not supported.")
                if member.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    raise DocumentProcessingError("A document package entry exceeds the size limit.")
                if member.file_size and not member.compress_size:
                    raise DocumentProcessingError("The document archive is invalid.")
                if member.compress_size and member.file_size / member.compress_size > MAX_ARCHIVE_EXPANSION_RATIO:
                    raise DocumentProcessingError("The document archive expands beyond the supported ratio.")
                total_uncompressed += member.file_size
                if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    raise DocumentProcessingError("The expanded document exceeds the size limit.")
                names.add(name)
            if required_member not in names:
                raise DocumentProcessingError("The document package is invalid or incomplete.")
    except DocumentProcessingError:
        raise
    except (BadZipFile, OSError, ValueError) as exc:
        raise DocumentProcessingError("The document package is invalid or could not be read.") from exc