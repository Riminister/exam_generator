# 🗂️ Project Reorganization Guide

## Overview

This reorganization creates a clean, logical structure:
- **`exam_generation/`** - Everything related to generating exams
- **`text_extraction/`** - PDF and question text extraction
- **`graph_extraction/`** - Graph analysis and recreation
- **`data_cleaning/`** - Data cleaning and validation

## How to Reorganize

### Step 1: Preview Changes (Dry Run)

```bash
# Using virtual environment
queens_exam_env\Scripts\python.exe scripts/reorganize_project.py --dry-run

# Or if python is in PATH
python scripts/reorganize_project.py --dry-run
```

This shows what will be moved without actually moving anything.

### Step 2: Execute Reorganization

```bash
# Remove --dry-run to actually move files
queens_exam_env\Scripts\python.exe scripts/reorganize_project.py

# Or
python scripts/reorganize_project.py
```

### Step 3: Review Changes

Check the new structure:
- Files moved to appropriate folders
- `__init__.py` files created for Python packages
- Documentation organized

### Step 4: Update Imports

Some imports may need updating. See `REORGANIZATION_NOTES.md` after running.

### Step 5: Run Tests

```bash
python tests/test_comprehensive.py
```

Fix any import errors that appear.

## New Structure Details

### exam_generation/
```
exam_generation/
├── openai/                    # OpenAI integration
│   ├── openai_question_generator.py
│   └── [OpenAI docs]
└── assembly/                  # Exam assembly
    └── generate_exam_from_data.py
```

### text_extraction/
```
text_extraction/
├── pdf_processing/            # PDF extraction
│   ├── extract_text_from_pdfs.py
│   ├── extract_cover_page_metadata.py
│   └── [extraction modules]
└── question_parsing/          # Question parsing
    ├── parse_questions_from_text.py
    ├── detect_question_types.py
    └── [parsing modules]
```

### graph_extraction/
```
graph_extraction/
├── analysis/                  # Graph analysis
│   ├── graph_analyzer.py
│   └── openai_question_analyzer.py
└── recreation/                # Graph recreation
    ├── graph_recreator.py
    └── graph_generator.py
```

### data_cleaning/
```
data_cleaning/
├── cleaners/                  # Cleaning modules
│   └── data_cleaner.py
├── validators/                 # Validation modules
│   ├── difficulty_calculator.py
│   └── calculate_difficulty.py
└── run_cleaning.py
```

## What Gets Moved

### Exam Generation Files
- `openai_question_generator.py` → `exam_generation/openai/`
- `generate_exam_from_data.py` → `exam_generation/assembly/`
- OpenAI documentation → `exam_generation/openai/`

### Text Extraction Files
- `extract_text_from_pdfs.py` → `text_extraction/pdf_processing/`
- `parse_questions_from_text.py` → `text_extraction/question_parsing/`
- `extract_cover_page_metadata.py` → `text_extraction/pdf_processing/`
- `detect_question_types.py` → `text_extraction/question_parsing/`
- Related modules from `exam_analysis/` → appropriate subfolders

### Graph Extraction Files
- `exam_analysis/graph_analyzer.py` → `graph_extraction/analysis/`
- `exam_analysis/graph_recreator.py` → `graph_extraction/recreation/`
- `exam_analysis/openai_question_analyzer.py` → `graph_extraction/analysis/`
- Integration scripts → `graph_extraction/`

### Data Cleaning Files
- `exam_analysis/data_cleaner.py` → `data_cleaning/cleaners/`
- `exam_analysis/difficulty_calculator.py` → `data_cleaning/validators/`
- `exam_analysis/run_cleaning.py` → `data_cleaning/`
- Data cleaning docs → `data_cleaning/`

## Import Updates Needed

After reorganization, update imports:

### Data Cleaner
```python
# Old
from exam_analysis.data_cleaner import ExamDataCleaner

# New
from data_cleaning.cleaners.data_cleaner import ExamDataCleaner
```

### Graph Analyzer
```python
# Old
from exam_analysis.graph_analyzer import GraphAnalyzer

# New
from graph_extraction.analysis.graph_analyzer import GraphAnalyzer
```

### Question Generator
```python
# Old
from openai_question_generator import OpenAIQuestionGenerator

# New
from exam_generation.openai.openai_question_generator import OpenAIQuestionGenerator
```

## Safety Features

- ✅ **Dry run mode** - Preview before executing
- ✅ **Checks for existing files** - Won't overwrite
- ✅ **Creates __init__.py** - Makes folders Python packages
- ✅ **Backup recommended** - Consider backing up before reorganizing

## Troubleshooting

### "File not found" errors
- Some files may not exist yet - that's OK
- Script handles missing files gracefully

### Import errors after reorganization
- Update imports as shown in `REORGANIZATION_NOTES.md`
- Or add to `sys.path` temporarily:
  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path(__file__).parent.parent))
  ```

### Files still in old locations
- Check if files were open in IDE
- Close all files and run again
- Some files may be intentionally kept in root

## Manual Reorganization (If Script Fails)

If the script doesn't work, you can manually:

1. Create folders:
   ```
   mkdir exam_generation exam_generation\openai exam_generation\assembly
   mkdir text_extraction text_extraction\pdf_processing text_extraction\question_parsing
   mkdir graph_extraction graph_extraction\analysis graph_extraction\recreation
   mkdir data_cleaning data_cleaning\cleaners data_cleaning\validators
   ```

2. Move files according to the mapping in the script

3. Create `__init__.py` files in each folder

## After Reorganization

1. ✅ Run tests: `python tests/test_comprehensive.py`
2. ✅ Fix any import errors
3. ✅ Update any scripts that reference old paths
4. ✅ Commit changes to version control

---

**Ready to reorganize?** Run with `--dry-run` first to preview!

