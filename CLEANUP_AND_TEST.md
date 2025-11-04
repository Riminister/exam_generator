# 🧹 Project Cleanup and Testing

## Overview

This guide helps you:
1. **Test everything** to ensure it works
2. **Clean up** the project structure
3. **Organize** files into proper directories

## Quick Start

### Step 1: Run Tests

```bash
# Using virtual environment
queens_exam_env\Scripts\python.exe run_all_tests.py

# Or using python directly
python run_all_tests.py
```

### Step 2: Organize Project

```bash
# Preview what will be organized (dry run)
python scripts/organize_project.py --dry-run

# Execute organization
python scripts/organize_project.py
```

## What Gets Tested

The comprehensive test suite verifies:

1. **Module Imports** - All Python modules can be imported
2. **Data Files** - Required data files exist and are valid JSON
3. **Data Cleaner** - Text cleaning works correctly
4. **Question Type Detection** - Can detect question types
5. **Difficulty Calculation** - Can calculate difficulty scores
6. **Question Parsing** - Can parse questions from text
7. **Exam Data Loading** - Can load exam data correctly
8. **OpenAI Setup** - OpenAI integration is configured (optional)
9. **Graph Recreation** - Can recreate graphs (optional)
10. **File Structure** - Project structure is correct

## What Gets Organized

### Files Moved to `scripts/`:
- `setup_openai.py`
- `integrate_openai_analysis.py`
- `integrate_graph_analysis.py`
- `generate_exam_from_data.py`
- `detect_question_types.py`
- `detect_translation_issues.py`
- `run_model_complete.py`

### Files Moved to `tests/`:
- `test_improved_model.py`

### Files Moved to `docs/guides/`:
- All `*_GUIDE.md` files
- All `QUICK_START*.md` files
- Workflow and feature documentation

### Files Moved to `outputs/`:
- Temporary output files
- Generated data files

## Project Structure After Cleanup

```
Parse_Files/
├── data/                    # Data files
├── exam_analysis/          # Core modules
├── models/                 # ML models
├── scripts/                # Utility scripts
├── tests/                  # Test suite
├── outputs/                # Generated outputs
├── docs/                   # Documentation
│   └── guides/            # How-to guides
└── notebooks/             # Jupyter notebooks
```

## Manual Cleanup (If Needed)

If scripts don't work, manually:

1. **Create directories**:
   ```bash
   mkdir scripts tests outputs docs\guides generated_graphs
   ```

2. **Move files** (review before moving):
   - Guides → `docs/guides/`
   - Utility scripts → `scripts/`
   - Test files → `tests/`

3. **Remove duplicates**:
   - Keep `sub_question_detector.py`, remove `detect_sub_questions.py` (if duplicate)

## Verification

After cleanup, verify:

```bash
# Run tests again
python run_all_tests.py

# Check structure
python -c "from pathlib import Path; print('✅ Structure OK' if Path('scripts').exists() else '❌ Structure needs fixing')"
```

## Troubleshooting

### Tests Fail
- Check data files exist
- Install dependencies: `pip install -r requirements.txt`
- Review error messages

### Organization Fails
- Check file permissions
- Ensure no files are open in other programs
- Review `--dry-run` output first

### Import Errors
- Ensure virtual environment is activated
- Check Python path
- Verify all modules are in correct locations

---

**Next Steps:**
1. ✅ Run tests: `python run_all_tests.py`
2. ✅ Review organization: `python scripts/organize_project.py --dry-run`
3. ✅ Execute organization: `python scripts/organize_project.py`
4. ✅ Verify: Run tests again

