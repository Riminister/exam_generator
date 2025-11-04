# ⚡ Quick Extract Guide

## Your PDFs are in `processed/` folder

**To extract them, just run:**

```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py
```

That's it! The script will:
1. ✅ Read all PDFs from `data/exam_downloads/processed/`
2. ✅ Extract text from each PDF
3. ✅ Save to `data/extracted_text.json`
4. ✅ Move processed PDFs to `to_process/` folder

## Other Options

**If PDFs are in `to_process/` instead:**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py --from-folder to_process
```

**Force OCR (for scanned PDFs):**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py --use-ocr
```

**Specify output file:**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py --output my_extracted_text.json
```

## After Extraction

**Parse questions:**
```bash
python text_extraction/question_parsing/parse_questions_from_text.py
```

This creates `data/exam_analysis.json` with structured questions.

