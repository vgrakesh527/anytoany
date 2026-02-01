# ✅ AnyToAny

**AnyToAny** is a production-quality image format conversion platform. It allows users to convert images from ANY supported format to ANY other format seamlessly via a clean, modern web interface.

## 🚀 Features

- **Format Support**: Convert between JPG, PNG, WEBP, BMP, TIFF, HEIC, and PDF.
- **Smart Logic**:
  - Single file upload → Downloads the converted file immediately.
  - Multiple files (Batch) → Downloads a ZIP archive containing all converted images.
- **Drag & Drop**: Modern upload interface with drag-and-drop support.
- **50-File Limit**: Enforces a maximum of 50 files per batch to ensure performance.
- **Security**: Validates MIME types, restricts extensions, and isolates user requests.
- **Auto-Cleanup**: Automatically removes temporary files after processing.

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/): High-performance web framework.
- [Pillow](https://python-pillow.org/): Powerful image processing library.
- [pillow-heif](https://pypi.org/project/pillow-heif/): HEIC format support.
- [Jinja2](https://jinja.palletsprojects.com/): Templating engine.

**Frontend**
- **HTML5 / CSS3**
- **Bootstrap 5**: Responsive and modern UI components.
- **Vanilla JavaScript**: Fetch API and DOM manipulation (No frameworks).

## 📂 Project Structure

```
app/
├── main.py                 # Application entry point
├── routes/
│   └── image_routes.py     # API endpoints
├── services/
│   ├── image_converter.py  # Image processing logic
│   ├── storage_service.py  # File I/O and security
│   ├── zip_service.py      # Archive creation
│   └── cleanup_service.py  # Temp file management
├── templates/
│   └── index.html          # Frontend UI
└── static/
    ├── css/
    └── js/
```

## ⚙️ Installation & Setup

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd anytoany
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access the Application**:
   Open your browser and visit: `http://127.0.0.1:8000`

## 📖 Usage Guide

1. **Upload**: Drag and drop images onto the upload zone or click "Browse Files".
   - *Note: Max 50 files per request.*
2. **Select Format**: Choose your desired output format from the dropdown (e.g., JPG, PNG, PDF).
3. **Convert**: Click the "Convert Files" button.
4. **Download**: 
   - If you uploaded one file, the converted image downloads automatically.
   - If you uploaded multiple files, a `converted_images.zip` file downloads automatically.

---
**AnyToAny** - Simple, Fast, and Modular.
