from PIL import Image, ImageOps
import pillow_heif
from pathlib import Path

# Register HEIF opener
pillow_heif.register_heif_opener()

class ImageConverter:
    @staticmethod
    def convert_image(input_path: Path, output_path: Path, target_format: str):
        """
        Convert image from input_path to output_path in target_format.
        """
        target_format = target_format.lower()
        # Pillow format names might differ slightly (e.g. 'jpeg' vs 'jpg')
        if target_format == 'jpg':
            save_format = 'JPEG'
        else:
            save_format = target_format.upper()

        try:
            with Image.open(input_path) as img:
                # Handle EXIF orientation
                img = ImageOps.exif_transpose(img)

                # Convert mode if necessary
                if save_format == 'JPEG':
                    if img.mode in ('RGBA', 'P', 'LA'):
                        img = img.convert('RGB')
                elif save_format == 'PDF':
                     if img.mode == 'RGBA':
                        img = img.convert('RGB')
                
                # Save
                # Quality can be adjusted, default is usually fine (75 for JPEG)
                save_kwargs = {}
                if save_format == 'JPEG':
                    save_kwargs['quality'] = 90
                    save_kwargs['optimize'] = True
                
                img.save(output_path, format=save_format, **save_kwargs)
                
        except Exception as e:
            raise ValueError(f"Failed to convert {input_path.name} to {target_format}: {str(e)}")
