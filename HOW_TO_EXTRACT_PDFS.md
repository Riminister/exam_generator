# 📄 How to Extract Text from PDFs

## Quick Answer

**If your PDFs are in `data/exam_downloads/processed/`:**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py
```

**If your PDFs are in `data/exam_downloads/to_process/`:**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py --from-folder to_process
```

## Folder Structure

```
data/exam_downloads/
├── to_process/      ← Put NEW PDFs here (or use processed/)
├── processed/       ← Script reads from here by default
└── README.txt
```

## Step-by-Step Process

### Step 1: Place PDFs in the Right Folder

**Option A: Use `processed/` folder (default)**
- Put PDFs in: `data/exam_downloads/processed/`
- Run script normally

**Option B: Use `to_process/` folder**
- Put PDFs in: `data/exam_downloads/to_process/`
- Run with: `python text_extraction/pdf_processing/extract_text_from_pdfs.py --from-folder to_process`

### Step 2: Run Extraction

```bash
# From project root
python text_extraction/pdf_processing/extract_text_from_pdfs.py
```

**What it does:**
1. ✅ Reads all PDFs from `processed/` folder (or specified folder)
2. ✅ Extracts text from each PDF
3. ✅ Uses OCR if needed (for scanned PDFs)
4. ✅ Saves results to `data/extracted_text.json`
5. ✅ Moves processed PDFs to `to_process/` folder

### Step 3: Parse Questions

After extraction, parse the questions:
```bash
python text_extraction/question_parsing/parse_questions_from_text.py
```

This creates `data/exam_analysis.json` with structured questions.

## Current Status

Based on your folders:
- `processed/` has 24 PDFs (ECON212 exams)
- `to_process/` has 39 PDFs (ECON110/111/112 exams)

**To extract the files in `processed/`:**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py
```

**To extract the files in `to_process/`:**
```bash
python text_extraction/pdf_processing/extract_text_from_pdfs.py --from-folder to_process
```

## Full Workflow

```bash
# 1. Extract text from PDFs
python text_extraction/pdf_processing/extract_text_from_pdfs.py

# 2. Parse into structured questions
python text_extraction/question_parsing/parse_questions_from_text.py

# 3. Clean the data (optional)
python data_cleaning/run_cleaning.py

# 4. Analyze with OpenAI (optional)
python graph_extraction/analysis/integrate_openai_analysis.py
```

## Troubleshooting

**"No PDFs found"**
- Check that PDFs are in the correct folder
- Use `--from-folder` to specify different folder

**OCR not working**
- Make sure Tesseract is installed
- Check `TESSERACT_CMD` environment variable

**Extraction fails**
- Check PDF file is not corrupted
- Try with `--use-ocr` flag for scanned PDFs

