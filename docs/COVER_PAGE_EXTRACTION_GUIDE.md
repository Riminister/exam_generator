# Cover Page Extraction & Context-Based OCR Guide

## 🎯 Overview

This guide explains the new scraping methods that extract metadata from exam cover pages and intelligently select OCR settings based on exam type.

---

## ✅ Features Implemented

### 1. **Cover Page Metadata Extraction**
Extracts from the first page of each exam PDF:
- ✅ **Course Code** (e.g., ECON310, ARAB100)
- ✅ **Course Name** (full descriptive name)
- ✅ **Faculty/Department** (e.g., "Faculty of Arts and Science")
- ✅ **Professor/Instructor** (instructor name)
- ✅ **Total Marks** (from cover page - more reliable than summing)
- ✅ **Exam Date** (with year, month, day, and relevance score)

### 2. **Date Extraction & Relevance Scoring**
- Extracts exam dates in various formats
- Calculates **relevance score** (0-1): newer exams = higher relevance
- Stores parsed date components for filtering

### 3. **Context-Based OCR Selection**
Automatically determines appropriate OCR settings:
- **Language Exams** (ARAB, FREN, etc.): Uses multi-language OCR (`ara+eng`, `fra+eng`)
- **Math Exams** (MATH, STAT, PHYS): Recommends MathPix or equation-aware OCR
- **General Exams**: Standard English OCR

---

## 🚀 Quick Start

### Step 1: Extract Cover Page Metadata

```bash
python extract_cover_page_metadata.py
```

This will:
1. Read all PDFs from `data/exam_downloads/`
2. Extract metadata from each cover page
3. Detect OCR context for each exam
4. Update `data/exam_analysis.json` with new fields

### Step 2: Re-calculate Difficulty Scores

After extraction, re-calculate difficulty scores to use cover page total marks:

```bash
python calculate_difficulty.py
```

The calculator now **prefers cover page total marks** over calculated sums (more accurate!).

---

## 📋 What Gets Added to exam_analysis.json

Each exam object will now include:

```json
{
  "filename": "ECON310.pdf",
  "course_code": "ECON310",
  "course_name": "Intermediate Microeconomics",  // NEW
  "faculty": "Faculty of Arts and Science",      // NEW
  "professor": "Dr. Smith",                       // NEW
  "total_marks_from_cover": 100,                  // NEW (from cover page)
  "exam_date": "2023-12-15",                      // NEW
  "exam_year": 2023,                               // NEW
  "exam_month": 12,                                // NEW
  "exam_day": 15,                                  // NEW
  "date_string": "December 15, 2023",             // NEW
  "relevance_score": 0.95,                         // NEW (newer = higher)
  "ocr_config": {                                  // NEW
    "ocr_language": "eng",
    "exam_type": "general",
    "needs_math_ocr": false,
    "detected_language": null,
    "recommended_ocr_method": "tesseract"
  },
  "questions": [...]
}
```

---

## 🔧 Module Details

### `exam_analysis/cover_page_parser.py`

**Main Class:** `CoverPageParser`

**Methods:**
- `extract_first_page_text(pdf_path)` - Gets first page text
- `extract_course_code(text)` - Finds course code
- `extract_course_name(text)` - Finds full course name
- `extract_faculty(text)` - Finds faculty/department
- `extract_professor(text)` - Finds instructor name
- `extract_total_marks(text)` - Finds total marks from cover
- `extract_date(text)` - Finds and parses exam date
- `parse_cover_page(pdf_path)` - Main method (does everything)

**Usage:**
```python
from exam_analysis.cover_page_parser import CoverPageParser

parser = CoverPageParser()
result = parser.parse_cover_page(Path("data/exam_downloads/ECON310.pdf"))

print(f"Course: {result['course_code']}")
print(f"Professor: {result['professor']}")
print(f"Total Marks: {result['total_marks']}")
```

---

### `exam_analysis/ocr_context_selector.py`

**Main Class:** `OCRContextSelector`

**Methods:**
- `detect_exam_type(course_code, first_page_text)` - Determines exam type
- `get_ocr_instructions(config)` - Gets human-readable instructions
- `should_re_extract(course_code, ocr_quality)` - Checks if re-extraction needed

**Supported Languages:**
- Arabic (ARAB) → `ara+eng`
- French (FREN) → `fra+eng`
- Spanish (SPAN) → `spa+eng`
- German (GERM) → `deu+eng`
- Chinese (CHIN) → `chi_sim+eng`
- Japanese (JAPA) → `jpn+eng`
- And more...

**Usage:**
```python
from exam_analysis.ocr_context_selector import OCRContextSelector

selector = OCRContextSelector()
config = selector.detect_exam_type("ARAB100")

print(f"OCR Language: {config['ocr_language']}")  # 'ara+eng'
print(f"Exam Type: {config['exam_type']}")          # 'language'
```

---

## 📊 Relevance Scoring

The relevance score indicates how current/relevant an exam is:

- **Score = 1.0**: Current year exam (most relevant)
- **Score = 0.5**: 10 years old
- **Score = 0.0**: 20+ years old (least relevant)

**Formula:**
```
relevance_score = max(0.0, min(1.0, 1.0 - (years_old / 20.0)))
```

**Use Cases:**
- Filter exams by relevance when generating questions
- Prioritize newer exams for training
- Weight exam importance in ML models

---

## 🔄 Integration with Difficulty Calculator

The difficulty calculator now uses cover page total marks when available:

```python
# OLD: Only summed question marks
total_marks = sum(all_question_marks)

# NEW: Prefers cover page, falls back to sum
total_marks = exam['total_marks_from_cover'] or sum(all_question_marks)
```

**Benefits:**
- More accurate total marks (cover page is authoritative)
- Works even if some questions missing marks
- Better difficulty score calculations

---

## 📝 Date Format Support

The parser supports many date formats:

- `December 15, 2023`
- `15/12/2023` or `12/15/2023`
- `2023-12-15`
- `Fall 2023` (seasonal)
- `2023` (year only)

All dates are parsed into structured format with ISO date string.

---

## 🎯 Best Practices

### 1. Run Extraction First
Always run cover page extraction before other processing:
```bash
python extract_cover_page_metadata.py
```

### 2. Then Re-calculate Difficulty
After extraction, re-run difficulty calculator to use new total marks:
```bash
python calculate_difficulty.py
```

### 3. Check OCR Recommendations
Review `ocr_config` field for each exam to see if re-extraction is recommended.

### 4. Filter by Relevance
Use `relevance_score` to prioritize newer exams:
```python
# In your code
recent_exams = [e for e in exams if e.get('relevance_score', 0) > 0.7]
```

---

## 🐛 Troubleshooting

### Issue: No metadata extracted

**Solutions:**
1. Check PDF has text layer (not just images)
2. Try different PDF extraction method
3. Verify first page format matches expected patterns

### Issue: Wrong course code detected

**Solutions:**
1. Check filename matches actual course code
2. Review first page text manually
3. Add custom pattern to `cover_page_parser.py`

### Issue: Date not parsed correctly

**Solutions:**
1. Date format may be non-standard
2. Check `date_string` field for raw value
3. Add new format pattern to parser

---

## 📈 Expected Results

After running extraction:

- **90%+** of exams should have course codes extracted
- **70%+** should have professor names
- **60%+** should have dates
- **50%+** should have total marks from cover page
- **100%** should have OCR config recommendations

---

## 🔗 Related Files

- `exam_analysis/cover_page_parser.py` - Core extraction logic
- `exam_analysis/ocr_context_selector.py` - OCR selection logic
- `extract_cover_page_metadata.py` - Main script
- `exam_analysis/difficulty_calculator.py` - Updated to use cover page marks
- `DIFFICULTY_SCORE_GUIDE.md` - Difficulty calculation guide

---

## 🚀 Next Steps

1. **Run extraction** on all your PDFs
2. **Review extracted metadata** for accuracy
3. **Re-calculate difficulty scores** with new total marks
4. **Use relevance scores** to filter/weight exams in ML models
5. **Follow OCR recommendations** for better extraction quality

---

**Questions?** Check the code comments or examine the extracted data in `exam_analysis.json`!

