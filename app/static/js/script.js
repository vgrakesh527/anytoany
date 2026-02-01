document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileCountText = document.getElementById('file-count-text');
    const convertBtn = document.getElementById('convert-btn');
    const uploadForm = document.getElementById('upload-form');
    const alertBox = document.getElementById('alert-box');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const processingMsg = document.getElementById('processing-msg');

    let selectedFiles = [];

    // Drag & Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        // Convert FileList to Array
        let newFiles = Array.from(files);

        // Filter out non-image files roughly (backend does real check)
        // newFiles = newFiles.filter(file => file.type.startsWith('image/') || file.name.toLowerCase().endsWith('.heic'));

        if (newFiles.length === 0) return;

        selectedFiles = newFiles; // Replace current selection or append? Requirement implies "Support multiple file selection" behavior often replaces in simple uploader
        // Let's replace for simplicity of state management, or if user browses again it usually replaces in standard inputs.

        updateUI();
    }

    function updateUI() {
        const count = selectedFiles.length;
        if (count > 0) {
            fileCountText.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
            convertBtn.disabled = false;

            // 2. File Limit Rule
            if (count > 50) {
                showAlert("warning", "AnyToAny supports a maximum of 50 images per conversion. The first 50 files will be processed.");
            } else {
                hideAlert();
            }
        } else {
            fileCountText.textContent = "No files selected";
            convertBtn.disabled = true;
            hideAlert();
        }
    }

    function showAlert(type, message) {
        alertBox.className = `alert alert-${type}`;
        alertBox.textContent = message;
        alertBox.classList.remove('d-none');
    }

    function hideAlert() {
        alertBox.classList.add('d-none');
    }

    // Form Submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (selectedFiles.length === 0) return;

        // UI Loading State
        convertBtn.disabled = true;
        btnText.textContent = ""; // Hide text? Or keep "Converting..."
        btnText.textContent = "Converting...";
        btnSpinner.classList.remove('d-none');
        processingMsg.classList.remove('d-none');

        const formData = new FormData();
        const targetFormat = document.getElementById('format-select').value;
        formData.append('target_format', targetFormat);

        // Limit to 50 allowed by backend logic, but we send all so backend can truncate/logic handles it
        // Or we truncate here? Requirement: "If user selects more than 50: Only process the first 50"
        // It's safer to send what user selected and let backend truncate or frontend truncate.
        // Let's frontend truncate to save bandwidth.
        const filesToSend = selectedFiles.slice(0, 50);

        filesToSend.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch('/upload-and-convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Conversion failed');
            }

            // Handle File Download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;

            // Get filename from header if possible, or guess
            const contentDisposition = response.headers.get('Content-Disposition');
            let fileName = 'converted_files';
            if (contentDisposition) {
                const fileNameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                if (fileNameMatch && fileNameMatch.length === 2)
                    fileName = fileNameMatch[1];
            }
            // Fallback for zipped vs single
            if (!fileName.includes('.')) {
                fileName += filesToSend.length > 1 ? '.zip' : `.${targetFormat}`;
            }

            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);

            showAlert('success', 'Conversion successful! Download started.');

            // Clear selected files after successful conversion
            selectedFiles = [];
            fileInput.value = ""; // Reset file input
            updateUI();

        } catch (error) {
            console.error(error);
            showAlert('danger', `Error: ${error.message}`);
        } finally {
            // Reset UI
            convertBtn.disabled = false;
            btnText.textContent = "Convert Files";
            btnSpinner.classList.add('d-none');
            processingMsg.classList.add('d-none');
        }
    });

    // dropZone click triggers input
    dropZone.addEventListener('click', () => fileInput.click());
});
