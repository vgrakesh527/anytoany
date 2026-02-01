import shutil
import os
import asyncio
from pathlib import Path

class CleanupService:
    @staticmethod
    async def remove_path(path: Path, delay: int = 0):
        """
        Remove a file or directory.
        Optionally wait for `delay` seconds before deleting (useful if file is being streamed).
        """
        if delay > 0:
            await asyncio.sleep(delay)
            
        try:
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")

    @staticmethod
    def cleanup_request_files(storage_service):
        """
        Cleanup the upload and converted directories for a specific request.
        This does not delete the final ZIP or File immediately if it's being returned,
        control that via background tasks in the route.
        """
        try:
            if storage_service.upload_path.exists():
                shutil.rmtree(storage_service.upload_path)
            if storage_service.converted_path.exists():
                shutil.rmtree(storage_service.converted_path)
            # Zips are in a separate dir, handled separately
        except Exception as e:
            print(f"Error cleaning up request directories: {e}")
