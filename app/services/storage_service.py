import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import List

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
CONVERTED_DIR = BASE_DIR / "converted"
ZIPS_DIR = BASE_DIR / "zips"

# Allowed extensions and mime types (can be expanded)
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp", ".heic"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def create_directories():
    """Ensure base directories exist."""
    UPLOAD_DIR.mkdir(exist_ok=True)
    CONVERTED_DIR.mkdir(exist_ok=True)
    ZIPS_DIR.mkdir(exist_ok=True)

class StorageService:
    def __init__(self):
        self.request_id = str(uuid.uuid4())
        self.upload_path = UPLOAD_DIR / self.request_id
        self.converted_path = CONVERTED_DIR / self.request_id
        
        # Ensure request-specific directories exist
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.converted_path.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> Path:
        """Save a single uploaded file to disk securely."""
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="Filename missing")
            
        # Basic sanitization: take basename and check extension
        safe_filename = Path(filename).name
        ext = Path(safe_filename).suffix.lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type {ext} not supported")
            
        file_path = self.upload_path / safe_filename
        
        # Write file
        try:
            size = 0
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    size += len(chunk)
                    if size > MAX_FILE_SIZE:
                        # Clean up partial file
                        buffer.close()
                        file_path.unlink(missing_ok=True)
                        raise HTTPException(status_code=413, detail=f"File {filename} exceeds 10MB limit")
                    buffer.write(chunk)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
            
        return file_path

    def get_converted_path(self, original_filename: str, target_format: str) -> Path:
        """Generate path for the converted file."""
        stem = Path(original_filename).stem
        # Map target format to extension
        ext_map = {
            "jpeg": ".jpg",
            "jpg": ".jpg",
            "png": ".png",
            "webp": ".webp",
            "bmp": ".bmp",
            "tiff": ".tiff",
            "pdf": ".pdf"
        }
        new_ext = ext_map.get(target_format.lower(), f".{target_format.lower()}")
        return self.converted_path / f"{stem}{new_ext}"

    def get_zip_path(self) -> Path:
        """Generate path for the output zip file."""
        # Zip files are stored in the main ZIP_DIR with uuid filename to avoid directory clutter
        # Or we can put them in the request folder. 
        # Requirement says /zips should be a base dir.
        return ZIPS_DIR / f"{self.request_id}.zip"
