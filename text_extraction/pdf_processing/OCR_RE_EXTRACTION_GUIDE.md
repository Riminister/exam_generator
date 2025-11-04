# OCR Re-Extraction Guide for Arabic & Translation Questions

## Problem
Some questions in your exams (especially ARAB100) contain garbled text because:
1. OCR was run **without Arabic language support**
2. OCR may have attempted **auto-translation** (converting Arabic → English)
3. The original Arabic text is lost and needs to be re-extracted

## Solution Options

### Option 1: Re-extract with Arabic OCR Support (Recommended)

If you still have the original PDF files, you can re-extract them with proper OCR settings.

#### Step 1: Install Tesseract with Arabic Language Pack

**Windows:**
```powershell
# Download Tesseract installer with language packs
# From: https://github.com/UB-Mannheim/tesseract/wiki
# Make sure to include "Arabic" language pack during installation

# Or use chocolatey:
choco install tesseract --params '/LanguagePacks:ara'
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # Arabic language pack
```

#### Step 2: Verify Arabic Support
```python
import pytesseract

# List available languages
print(pytesseract.get_languages())

# Should include 'ara' (Arabic)
```

#### Step 3: Re-extract with Arabic Language

Create a re-extraction script:

```python
import pytesseract
from PIL import Image
import pdf2image

# Convert PDF to images
images = pdf2image.convert_from_path('data/exam_downloads/ARAB100.pdf')

# Extract text with Arabic language
for i, image in enumerate(images):
    # Use Arabic language: 'ara'
    # Use both Arabic and English: 'ara+eng'
    text = pytesseract.image_to_string(image, lang='ara+eng')
    print(f"Page {i+1}:\n{text}\n")
```

**Key Settings:**
- `lang='ara'` - Arabic only
- `lang='ara+eng'` - Arabic + English (for mixed-language exams)
- `config='--psm 6'` - Assume uniform block of text (may help with Arabic)

#### Step 4: Update Question Text
After re-extraction, manually update the question text in `data/exam_analysis.json` for questions marked with:
- `needs_re_extraction: true`
- `ocr_language_needed: "arabic"`

---

### Option 2: Use Cloud OCR Services (Alternative)

If local OCR doesn't work well, consider cloud services with better Arabic support:

#### Google Cloud Vision API
```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()
response = client.text_detection(image=image)
# Better Arabic support than Tesseract
```

#### AWS Textract
- Better multilingual support
- Handles Arabic well
- Paid service

#### Azure Computer Vision
- Good Arabic OCR
- API available

---

### Option 3: Manual Correction (For Few Questions)

If only a few questions are affected, you can manually correct them:

1. Open the original PDF (`data/exam_downloads/ARAB100.pdf`)
2. Find the question with poor OCR
3. Copy the correct Arabic text
4. Update `data/exam_analysis.json` directly

**Example:**
```json
{
  "question_number": 14,
  "text": "IV. Translate into ENGLISH: (15pts.)\n\n[MANUALLY INSERT CORRECT ARABIC TEXT HERE]",
  "needs_re_extraction": false,
  "ocr_quality": "corrected"
}
```

---

### Option 4: Use Alternative PDF Extraction (If PDF Has Text Layer)

Some PDFs have selectable text (not scanned images):

```python
import pdfplumber

with pdfplumber.open('data/exam_downloads/ARAB100.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        # This preserves original Arabic if PDF has text layer
        print(text)
```

**Check if PDF has text layer:**
- Try selecting text in PDF viewer
- If you can copy Arabic text → PDF has text layer → use `pdfplumber`
- If text can't be selected → it's scanned → need OCR

---

## Identifying Questions That Need Re-Extraction

After running `python detect_translation_issues.py`, questions will be marked:

```json
{
  "question_number": 14,
  "text": "IV. Translate into ENGLISH: (15pts.)\nAan YG ll 9 Alsen oh GAM...",
  "is_translation_question": true,
  "has_poor_ocr": true,
  "needs_re_extraction": true,
  "ocr_priority": "high",
  "target_language": "Arabic",
  "ocr_language_needed": "arabic"
}
```

**Filter questions needing re-extraction:**
```python
import json

with open('data/exam_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for exam in data['exams']:
    for q in exam['questions']:
        if q.get('needs_re_extraction'):
            print(f"Question {q['question_number']}: {q['text'][:100]}...")
            print(f"  Language needed: {q.get('ocr_language_needed', 'unknown')}")
            print(f"  Priority: {q.get('ocr_priority', 'unknown')}\n")
```

---

## Recommended Workflow

1. **Run detection:**
   ```bash
   python detect_translation_issues.py
   ```

2. **Review flagged questions:**
   - Check `ocr_priority: "high"` questions first
   - These are translation questions with poor OCR

3. **Re-extract with proper language:**
   - Use Arabic OCR (`lang='ara+eng'`)
   - Update JSON file with corrected text

4. **Re-run data cleaning:**
   ```bash
   python exam_analysis/run_cleaning.py
   ```

5. **Verify in EDA notebook:**
   - Check that Arabic text is now readable
   - Verify translation questions have proper source text

---

## Preventing Future Issues

When extracting new exams:

1. **Detect exam language first:**
   - Check course code (ARAB = Arabic, FREN = French, etc.)
   - Configure OCR language accordingly

2. **Use multi-language OCR:**
   ```python
   pytesseract.image_to_string(image, lang='ara+eng')  # Arabic + English
   ```

3. **Never enable auto-translation:**
   - OCR should extract text, NOT translate it
   - Translation is a separate step (if needed)

4. **Test OCR quality:**
   - Run `detect_translation_issues.py` after extraction
   - Fix issues before proceeding to analysis

---

## Example Re-Extraction Script

See `scripts/re_extract_arabic.py` (create if needed) for a complete re-extraction example.

