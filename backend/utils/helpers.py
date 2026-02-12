import os
from pathlib import Path

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def save_upload_file(upload_file, destination: str) -> str:
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(upload_file.file.read())
    return str(dest_path)
