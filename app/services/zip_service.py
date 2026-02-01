import zipfile
from pathlib import Path
from typing import List

class ZipService:
    @staticmethod
    def create_zip(files: List[Path], output_zip_path: Path):
        """
        Create a zip file containing the specified files.
        """
        try:
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files:
                    if file_path.exists():
                        # Store file in zip with just its filename, not full path
                        zf.write(file_path, arcname=file_path.name)
        except Exception as e:
            raise ValueError(f"Failed to create zip file: {str(e)}")
