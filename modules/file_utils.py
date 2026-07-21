import zipfile
from io import BytesIO
from pathlib import Path


ALREADY_COMPRESSED_SUFFIXES = frozenset(
    {
        ".avi",
        ".bmp",
        ".gif",
        ".jpeg",
        ".jpg",
        ".m4a",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".png",
        ".webp",
        ".xlsx",
        ".xlsm",
        ".zip",
    }
)


def deduplicate_filenames(named_data):
    name_counts = {}
    deduplicated = []

    for filename, data in named_data:
        duplicate_index = name_counts.get(filename, 0)
        if duplicate_index:
            path = Path(filename)
            unique_name = f"{path.stem} ({duplicate_index}){path.suffix}"
        else:
            unique_name = filename

        name_counts[filename] = duplicate_index + 1
        deduplicated.append((unique_name, data))

    return deduplicated


def zip_compression_for_filename(filename):
    suffix = Path(filename).suffix.lower()
    if suffix in ALREADY_COMPRESSED_SUFFIXES:
        return zipfile.ZIP_STORED
    return zipfile.ZIP_DEFLATED


def build_zip_bytes(named_data):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        for filename, data in named_data:
            archive.writestr(
                filename,
                data,
                compress_type=zip_compression_for_filename(filename),
            )
    return zip_buffer.getvalue()
