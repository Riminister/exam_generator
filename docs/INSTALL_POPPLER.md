# Installing Poppler for OCR on Windows

## Why Do I Need Poppler?

Poppler is required by `pdf2image` to convert PDF pages to images for OCR processing. On Windows, poppler must be explicitly installed and configured.

## Error Message

If you see:
```
OCR failed: Unable to get page count. Is poppler installed and in PATH?
```

This means poppler is not found or not configured correctly.

## Installation Options

### Option 1: Download Pre-built Poppler (Recommended)

1. **Download Poppler for Windows:**
   - Go to: https://github.com/oschwartz10612/poppler-windows/releases/
   - Download the latest release (e.g., `Release-25.07.0-0.zip`)
   - Extract the ZIP file

2. **Place in Project Directory:**
   ```
   text_extraction/pdf_processing/poppler/bin/
   ```
   The `bin` folder should contain `pdftoppm.exe` and other poppler executables.

3. **Or Set Environment Variable:**
   ```powershell
   # In PowerShell (permanent)
   [System.Environment]::SetEnvironmentVariable('POPPLER_PATH', 'C:\path\to\poppler\bin', 'User')
   ```

### Option 2: Use Chocolatey (Windows Package Manager)

```powershell
choco install poppler
```

Then add to PATH or set environment variable:
```powershell
$env:POPPLER_PATH = "C:\ProgramData\chocolatey\lib\poppler\tools"
```

### Option 3: Install via Conda (If Using Anaconda)

```bash
conda install -c conda-forge poppler
```

## Verification

After installation, verify poppler works:

```python
from pathlib import Path
import sys

poppler_path = Path("text_extraction/pdf_processing/poppler/bin")
if (poppler_path / "pdftoppm.exe").exists():
    print("✅ Poppler found!")
else:
    print("❌ Poppler not found")
```

## Project Structure

The script automatically looks for poppler in these locations:

1. `POPPLER_PATH` environment variable
2. `text_extraction/pdf_processing/Release-25.07.0-0/poppler-25.07.0/Library/bin/`
3. `text_extraction/pdf_processing/poppler/bin/`
4. `text_extraction/pdf_processing/poppler/Library/bin/`

## Troubleshooting

### "Poppler path found but pdftoppm not found"

**Solution:** Make sure the `bin` folder contains `pdftoppm.exe` (or `pdftoppm` on Linux/Mac).

### "Poppler not found"

**Solution:** 
1. Download poppler from the GitHub releases page
2. Extract to one of the project locations above
3. Or set `POPPLER_PATH` environment variable

### OCR Still Fails After Installing Poppler

**Check:**
1. Is poppler path correct? Run: `python -c "from pathlib import Path; print(Path('text_extraction/pdf_processing/poppler/bin').exists())"`
2. Does `pdftoppm.exe` exist in the bin folder?
3. Try setting `POPPLER_PATH` explicitly:
   ```python
   import os
   os.environ['POPPLER_PATH'] = r'C:\path\to\poppler\bin'
   ```

## Alternative: Skip OCR

If you don't need OCR (for text-based PDFs), the extraction will work without poppler by using:
- `pdfplumber` (for PDFs with text layer)
- `pymupdf` (alternative text extraction)

OCR is only needed for scanned PDFs (images without text layer).

