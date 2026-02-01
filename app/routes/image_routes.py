from fastapi import APIRouter, UploadFile, Form, File, HTTPException, BackgroundTasks
from typing import List, Optional
from fastapi.responses import FileResponse
from app.services.storage_service import StorageService
from app.services.image_converter import ImageConverter
from app.services.zip_service import ZipService
from app.services.cleanup_service import CleanupService
import shutil
from pathlib import Path

router = APIRouter()

@router.post("/upload-and-convert")
async def upload_and_convert(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    target_format: str = Form(...)
):
    """
    Handle image upload and conversion.
    """
    # 2. File Limit Rule
    # Only process first 50 files
    files_to_process = files[:50]
    
    storage = StorageService()
    
    try:
        saved_files = []
        # Save files
        for file in files_to_process:
            saved_path = await storage.save_upload(file)
            saved_files.append(saved_path)
            
        converted_files = []
        # Convert files
        for input_path in saved_files:
            output_path = storage.get_converted_path(input_path.name, target_format)
            ImageConverter.convert_image(input_path, output_path, target_format)
            converted_files.append(output_path)
            
        if not converted_files:
             raise HTTPException(status_code=400, detail="No files converted")

        # 5. Conversion Result Logic
        if len(converted_files) == 1:
            # Return single file
            file_to_return = converted_files[0]
            filename = file_to_return.name
            
            # Schedule cleanup
            # We need to cleanup the entire request folder (uploads AND converted) after response
            # But specific file to return must exist until response is sent.
            # FileResponse opens the file, so we can clean up parent dirs?
            # Actually, standard practice: return file, and use background task to clean up.
            
            background_tasks.add_task(CleanupService.cleanup_request_files, storage)
            
            # Note: FileResponse might keep file handle open. 
            # Ideally we might move it to a temp location or handle cleanup carefully.
            # But for simplicity, we pass `background_tasks` to clean directories. 
            # Since FileResponse reads file, we should verify if cleaning dir mid-read is issue.
            # Usually safe if we just let it finish. But to be safe, we can add a small delay
            # or rely on OS to delete after handle close if we were using tempfile, but we are using paths.
            # Let's rely on standard background task functionality.
            
            return FileResponse(
                path=file_to_return, 
                filename=filename, 
                media_type='application/octet-stream'
            )
            
        else:
            # Create ZIP
            zip_path = storage.get_zip_path()
            ZipService.create_zip(converted_files, zip_path)
            
            # Schedule cleanup of request dirs AND the zip file itself
            background_tasks.add_task(CleanupService.cleanup_request_files, storage)
            background_tasks.add_task(CleanupService.remove_path, zip_path, delay=10) # Give 10s delay just in case? Or just standard.
            
            return FileResponse(
                path=zip_path,
                filename=f"converted_images.zip",
                media_type='application/zip'
            )

    except Exception as e:
        # cleanup on error
        CleanupService.cleanup_request_files(storage)
        raise HTTPException(status_code=500, detail=str(e))
