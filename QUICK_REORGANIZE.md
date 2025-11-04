# ⚡ Quick Reorganization Guide

## Run This

```bash
# Preview first (recommended)
queens_exam_env\Scripts\python.exe scripts/reorganize_project.py --dry-run

# Then execute
queens_exam_env\Scripts\python.exe scripts/reorganize_project.py
```

## What It Does

Creates these folders and moves files:

```
✅ exam_generation/          - Exam generation (OpenAI, assembly)
✅ text_extraction/          - PDF and question extraction  
✅ graph_extraction/         - Graph analysis and recreation
✅ data_cleaning/            - Data cleaning and validation
```

## After Reorganization

1. **Update imports** (see REORGANIZATION_NOTES.md)
2. **Run tests**: `python tests/test_comprehensive.py`
3. **Fix any errors** that appear

That's it! 🎉

