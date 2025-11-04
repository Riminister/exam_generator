# 🧪 Quick Test Guide

## Run All Tests

```bash
# Using virtual environment
queens_exam_env\Scripts\python.exe run_all_tests.py

# Or if python is in PATH
python run_all_tests.py
```

## Individual Test Components

### 1. Test Imports
```python
python -c "import extract_text_from_pdfs; import parse_questions_from_text; print('✅ Imports OK')"
```

### 2. Test Data Files
```python
python -c "import json; json.load(open('data/exam_analysis.json')); print('✅ Data files OK')"
```

### 3. Test Modules
```python
python -c "from exam_analysis.data_cleaner import ExamDataCleaner; print('✅ Data cleaner OK')"
```

## Test Suite Coverage

The comprehensive test suite checks:
- ✅ Module imports
- ✅ Data file existence and validity
- ✅ Data cleaner functionality
- ✅ Question type detection
- ✅ Difficulty calculation
- ✅ Question parsing
- ✅ Exam data loading
- ✅ OpenAI setup (if configured)
- ✅ Graph recreation (if matplotlib available)
- ✅ File structure

## Expected Results

All tests should pass if:
1. Data files exist (`data/exam_analysis.json`, `data/extracted_text.json`)
2. Required modules are installed
3. Project structure is correct

## Troubleshooting

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Check virtual environment is activated

### "Data file not found"
- Run extraction pipeline first:
  ```bash
  python extract_text_from_pdfs.py
  python parse_questions_from_text.py
  ```

### "OpenAI test failed"
- This is optional - OpenAI integration is optional
- Set up OpenAI: `python scripts/setup_openai.py`

