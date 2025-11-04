# 📁 Folder Structure Guide: Processed vs To-Process

## 🎯 New Folder Structure

Your `exam_downloads` folder is now organized into two subfolders:

```
data/exam_downloads/
├── to_process/          # 📥 PDFs waiting to be extracted
│   ├── ARAB100.pdf
│   ├── ECON310.pdf
│   └── ... (21 PDFs)
│
└── processed/           # ✅ PDFs that have been extracted
    └── (empty initially, fills as you process)
```

## 🚀 How It Works

### **Automatic Processing:**

1. **Place new PDFs** in `data/exam_downloads/to_process/`
2. **Run extraction**: `python extract_text_from_pdfs.py`
3. **Script automatically**:
   - Processes PDFs from `to_process/`
   - Extracts text
   - **Moves successful PDFs** to `processed/`
   - Leaves failed PDFs in `to_process/` (so you can retry)

### **Benefits:**

✅ **No duplicate processing** - PDFs are moved after extraction
✅ **Easy tracking** - See what's done vs what's pending
✅ **Safe retries** - Failed extractions stay in `to_process/` for debugging

## 📋 Usage Examples

### Extract All Pending PDFs:
```bash
python extract_text_from_pdfs.py
```

### Extract with OCR (for scanned PDFs):
```bash
python extract_text_from_pdfs.py --ocr
```

### Check Status:
```bash
# See how many are pending vs processed
python verify_folder_setup.py
```

## 🔄 Manual Folder Management

### To Re-process an Exam:
```bash
# Move PDF back to to_process folder
move data/exam_downloads/processed/ARAB100.pdf data/exam_downloads/to_process/
```

### To Add New Exams:
1. Place PDFs in `data/exam_downloads/to_process/`
2. Run extraction script

## ⚠️ Important Notes

- **Only successful extractions are moved** to `processed/`
- **Failed extractions stay** in `to_process/` so you can fix and retry
- **The script creates folders automatically** if they don't exist
- **README.txt stays in base folder** (not moved)

## 🎯 Multiple Choice Question Type Added

The system now detects `multiple_choice` questions automatically!

**Detection criteria:**
- Questions with 2+ option markers (A), B), C), D), E))
- Common MC phrases ("choose the best", "which of the following")
- Option patterns: `A)`, `(a)`, `a.`, etc.

**To detect question types in existing data:**
```bash
python detect_question_types.py
```

This will:
- Detect `multiple_choice`, `true_false`, `numerical`, `essay`, `short_answer`
- Update `exam_analysis.json` with correct types
- Extract options from multiple choice questions during cleaning

---

**Your folder structure is ready! Start processing with:**
```bash
python extract_text_from_pdfs.py
```

