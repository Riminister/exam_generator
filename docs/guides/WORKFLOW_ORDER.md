# 📋 Correct Order of Operations

## The Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Extract Text from PDFs                             │
│  python extract_text_from_pdfs.py                           │
│  Input:  PDFs in data/exam_downloads/to_process/            │
│  Output: data/extracted_text.json (raw text)                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Parse Questions from Text ⭐ YOU ARE HERE          │
│  python parse_questions_from_text.py                         │
│  Input:  data/extracted_text.json                            │
│  Output: data/exam_analysis.json (structured questions)     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Clean the Data                                      │
│  python exam_analysis/data_cleaner.py                       │
│  Input:  data/exam_analysis.json                            │
│  Output: exam_analysis/cleaned_questions.json                │
└─────────────────────────────────────────────────────────────┘
```

## What Each Step Does

### Step 1: `extract_text_from_pdfs.py`
- **What it does**: Takes PDF files and extracts raw text (using OCR if needed)
- **Creates**: `data/extracted_text.json` with raw text blocks
- **You have**: ✅ This file exists

### Step 2: `parse_questions_from_text.py` ⭐ **RUN THIS NEXT!**
- **What it does**: Takes the raw text and splits it into individual questions
- **Creates**: `data/exam_analysis.json` with structured question objects
- **You need**: ❌ This file is empty/missing - **This is why data_cleaner.py fails!**

### Step 3: `data_cleaner.py`
- **What it does**: Cleans, validates, and removes duplicates from questions
- **Needs**: `data/exam_analysis.json` (created by step 2)
- **Creates**: `exam_analysis/cleaned_questions.json`

## Quick Fix

Run this command to create the missing file:

```bash
python parse_questions_from_text.py
```

Then you can run:

```bash
python exam_analysis/data_cleaner.py
```

## Why This Happens

- `extracted_text.json` = **Raw text** (like a big text document)
- `exam_analysis.json` = **Structured questions** (individual question objects)
- `data_cleaner.py` expects structured questions, not raw text!

That's why you got the error: the cleaner needs `exam_analysis.json`, but it's empty because you haven't run the parser yet.

