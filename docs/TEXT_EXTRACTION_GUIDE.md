# Text Extraction Guide

## 🎯 Overview

This guide explains how to extract text (words) from PDF exam files using the new text extraction utilities.

---

## 📚 Methods Available

### 1. **Extract Text from Single PDF**

```python
from exam_analysis.text_extractor import extract_text_from_exam
from pathlib import Path

# Extract text (automatically detects OCR settings)
result = extract_text_from_exam(
    pdf_path=Path("data/exam_downloads/ARAB100.pdf"),
    course_code="ARAB100",  # Optional: helps with OCR selection
    use_ocr=False  # Set True to force OCR
)

if result['success']:
    print(f"Extracted {len(result['text'])} characters")
    print(f"Method: {result['extraction_method']}")  # 'pdfplumber', 'pymupdf', or 'ocr'
    print(f"Pages: {len(result['pages'])}")
```

### 2. **Extract Words from Text**

```python
from exam_analysis.text_extractor import TextExtractor

extractor = TextExtractor()

# Extract all words
text = "This is a sample question with multiple words."
words = extractor.extract_words(text)
# Result: ['This', 'is', 'a', 'sample', 'question', 'with', 'multiple', 'words']

# Extract unique words (no duplicates)
unique_words = extractor.extract_unique_words(text, lowercase=True)
# Result: ['a', 'is', 'multiple', 'question', 'sample', 'this', 'with', 'words']

# Options
words = extractor.extract_words(
    text,
    min_length=3,        # Minimum word length
    remove_numbers=True, # Remove pure numbers
    lowercase=True       # Convert to lowercase
)
```

### 3. **Get Text Statistics**

```python
from exam_analysis.text_extractor import TextExtractor

extractor = TextExtractor()
text = "Your extracted text here..."

stats = extractor.extract_text_statistics(text)
print(f"Total words: {stats['total_words']}")
print(f"Unique words: {stats['unique_words']}")
print(f"Average word length: {stats['avg_word_length']:.2f}")
print(f"Average sentence length: {stats['avg_sentence_length']:.2f}")
```

### 4. **Bulk Extract from All PDFs**

```bash
# Extract text from all PDFs (no OCR)
python extract_text_from_pdfs.py

# Extract with OCR (for scanned PDFs)
python extract_text_from_pdfs.py --ocr
```

This will:
- Extract text from all PDFs in `data/exam_downloads/`
- Automatically detect course codes from filenames
- Select appropriate OCR settings for each exam
- Save results to `data/extracted_text.json`

---

## 🔧 Usage Examples

### Example 1: Extract Text from One Exam

```python
from pathlib import Path
from exam_analysis.text_extractor import extract_text_from_exam

pdf_path = Path("data/exam_downloads/ECON310.pdf")
result = extract_text_from_exam(pdf_path, course_code="ECON310")

if result['success']:
    # Get full text
    full_text = result['text']
    
    # Get text per page
    for i, page_text in enumerate(result['pages'], 1):
        print(f"Page {i}: {len(page_text)} characters")
    
    # Get extraction method used
    print(f"Method: {result['extraction_method']}")
```

### Example 2: Extract and Analyze Words

```python
from exam_analysis.text_extractor import TextExtractor

extractor = TextExtractor()

# Extract text from PDF
result = extractor.extract_text_from_pdf(
    Path("data/exam_downloads/ARAB100.pdf"),
    course_code="ARAB100"
)

if result['success']:
    # Extract all words
    words = extractor.extract_words(result['text'])
    print(f"Total words: {len(words)}")
    
    # Get unique words
    unique_words = extractor.extract_unique_words(result['text'])
    print(f"Unique words: {len(unique_words)}")
    
    # Get statistics
    stats = extractor.extract_text_statistics(result['text'])
    print(f"Average word length: {stats['avg_word_length']:.2f}")
```

### Example 3: Extract with OCR (for Scanned PDFs)

```python
from exam_analysis.text_extractor import TextExtractor

extractor = TextExtractor()

# Force OCR usage
result = extractor.extract_text_from_pdf(
    Path("data/exam_downloads/ARAB100.pdf"),
    use_ocr=True,
    course_code="ARAB100"  # Automatically uses 'ara+eng' OCR
)

if result['success']:
    print(f"Extracted using OCR: {result['extraction_method']}")
    print(f"OCR config: {result['ocr_config']}")
```

---

## 📊 Extraction Methods

The extractor tries three methods in order:

1. **pdfplumber** (for PDFs with text layer)
   - Fastest
   - Preserves formatting
   - Best for digital PDFs

2. **PyMuPDF** (fallback for text layer)
   - Good alternative
   - Also preserves formatting

3. **OCR** (for scanned PDFs or when requested)
   - Uses Tesseract
   - Automatically selects language based on course code
   - Slower but works for scanned documents

---

## 🌍 OCR Language Selection

The extractor automatically selects OCR language based on course code:

- **ARAB** → Arabic + English (`ara+eng`)
- **FREN** → French + English (`fra+eng`)
- **SPAN** → Spanish + English (`spa+eng`)
- **MATH/STAT/PHYS** → English (may need MathPix for equations)
- **Other** → English (`eng`)

You can override:
```python
result = extractor.extract_text_from_pdf(
    pdf_path,
    use_ocr=True,
    ocr_language='ara+eng'  # Override auto-detection
)
```

---

## 📝 Output Format

### Single PDF Extraction

```python
result = {
    'text': 'Full extracted text...',
    'pages': ['Page 1 text...', 'Page 2 text...'],
    'extraction_method': 'pdfplumber',  # or 'pymupdf' or 'ocr'
    'ocr_config': {
        'ocr_language': 'eng',
        'exam_type': 'general',
        ...
    },
    'success': True
}
```

### Bulk Extraction JSON

```json
{
  "extractions": [
    {
      "filename": "ECON310.pdf",
      "course_code": "ECON310",
      "extraction_method": "pdfplumber",
      "num_pages": 5,
      "text_length": 12345,
      "num_words": 2345,
      "num_unique_words": 456,
      "statistics": {
        "total_chars": 12345,
        "total_words": 2345,
        "avg_word_length": 5.2
      },
      "text": "Full text...",
      "pages": ["Page 1...", "Page 2..."]
    }
  ],
  "stats": {
    "total_pdfs": 13,
    "successful": 12,
    "failed": 1,
    "used_ocr": 2
  }
}
```

---

## 🔍 Common Use Cases

### Extract Words from Questions

```python
import json
from exam_analysis.text_extractor import TextExtractor

# Load exam data
with open('data/exam_analysis.json', 'r') as f:
    data = json.load(f)

extractor = TextExtractor()

# Extract words from all questions
all_words = []
for exam in data['exams']:
    for question in exam['questions']:
        question_text = question.get('text', '')
        words = extractor.extract_words(question_text, lowercase=True)
        all_words.extend(words)

# Get unique words
unique_words = sorted(set(all_words))
print(f"Total unique words across all questions: {len(unique_words)}")
```

### Analyze Text from One Exam

```python
from exam_analysis.text_extractor import extract_text_from_exam
from pathlib import Path

result = extract_text_from_exam(Path("data/exam_downloads/ECON310.pdf"))

if result['success']:
    extractor = TextExtractor()
    stats = extractor.extract_text_statistics(result['text'])
    
    print(f"📊 Exam Statistics:")
    print(f"   Total words: {stats['total_words']:,}")
    print(f"   Unique words: {stats['unique_words']:,}")
    print(f"   Average word length: {stats['avg_word_length']:.2f}")
    print(f"   Average sentence length: {stats['avg_sentence_length']:.2f}")
```

---

## 🐛 Troubleshooting

### Issue: Text extraction returns empty

**Solutions:**
1. Try OCR mode:
   ```python
   result = extractor.extract_text_from_pdf(pdf_path, use_ocr=True)
   ```

2. Check if PDF has text layer:
   - Open PDF in viewer
   - Try to select/copy text
   - If you can't → PDF is scanned → use OCR

3. Check PDF is not corrupted

### Issue: OCR not working

**Solutions:**
1. Install required packages:
   ```bash
   pip install pytesseract pdf2image
   ```

2. Install Tesseract OCR:
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

3. Verify language packs installed:
   ```python
   import pytesseract
   print(pytesseract.get_languages())
   ```

### Issue: Wrong language OCR

**Solutions:**
1. Specify course code (auto-detects language):
   ```python
   result = extractor.extract_text_from_pdf(
       pdf_path,
       course_code="ARAB100"  # Auto-selects Arabic OCR
   )
   ```

2. Manually specify language:
   ```python
   result = extractor.extract_text_from_pdf(
       pdf_path,
       use_ocr=True,
       ocr_language='ara+eng'  # Arabic + English
   )
   ```

---

## 📚 Related Files

- `exam_analysis/text_extractor.py` - Core text extraction module
- `extract_text_from_pdfs.py` - Bulk extraction script
- `exam_analysis/ocr_context_selector.py` - OCR language selection
- `exam_analysis/cover_page_parser.py` - Cover page extraction

---

## 🚀 Quick Start

1. **Extract text from one PDF:**
   ```python
   from exam_analysis.text_extractor import extract_text_from_exam
   from pathlib import Path
   
   result = extract_text_from_exam(Path("data/exam_downloads/ECON310.pdf"))
   print(result['text'])
   ```

2. **Extract words:**
   ```python
   from exam_analysis.text_extractor import TextExtractor
   
   extractor = TextExtractor()
   words = extractor.extract_words("Your text here")
   ```

3. **Bulk extract all PDFs:**
   ```bash
   python extract_text_from_pdfs.py
   ```

---

**Ready to extract text!** 🎉

