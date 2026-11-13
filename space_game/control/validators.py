from pathlib import Path

from filer.validation import deny


def validate_binary_download(file_name, file, owner, mime_type):
    # Filer treats Windows installers and AppImages as octet-stream. Enable
    # these website download formats without relaxing HTML/XML/SVG validation.
    if Path(file_name).suffix.lower() not in {
        ".exe",
        ".msi",
        ".appimage",
        ".zip",
        ".7z",
        ".gz",
        ".xz",
        ".bz2",
        ".deb",
        ".rpm",
    }:
        deny(file_name, file, owner, mime_type)
