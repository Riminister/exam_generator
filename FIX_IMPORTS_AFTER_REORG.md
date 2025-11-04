# 🔧 Fix Imports After Reorganization

## Files That Need Import Updates

After reorganization, several files still have old import paths. Here's what needs to be fixed:

### 1. `text_extraction/pdf_processing/extract_text_from_pdfs.py`

**Current (line 15):**
```python
from exam_analysis.text_extractor import TextExtractor, extract_text_from_exam
```

**Should be:**
```python
from text_extraction.pdf_processing.text_extractor import TextExtractor, extract_text_from_exam
```

### 2. `text_extraction/question_parsing/parse_questions_from_text.py`

**Current (lines 13-14):**
```python
from exam_analysis.question_type_detector import QuestionTypeDetector
from exam_analysis.difficulty_calculator import DifficultyCalculator
```

**Should be:**
```python
from text_extraction.question_parsing.question_type_detector import QuestionTypeDetector
from data_cleaning.validators.difficulty_calculator import DifficultyCalculator
```

### 3. Any files importing from `exam_analysis/`

Check all files for imports like:
- `from exam_analysis import ...`
- `from exam_analysis.xxx import ...`

Update to new paths:
- `exam_analysis.data_cleaner` → `data_cleaning.cleaners.data_cleaner`
- `exam_analysis.question_type_detector` → `text_extraction.question_parsing.question_type_detector`
- `exam_analysis.difficulty_calculator` → `data_cleaning.validators.difficulty_calculator`
- `exam_analysis.graph_analyzer` → `graph_extraction.analysis.graph_analyzer`
- `exam_analysis.graph_recreator` → `graph_extraction.recreation.graph_recreator`

## Quick Fix Script

Run this to find all files with old imports:

```python
import re
from pathlib import Path

old_patterns = [
    r'from exam_analysis\.',
    r'import exam_analysis',
]

for py_file in Path('.').rglob('*.py'):
    if 'queens_exam_env' in str(py_file) or '__pycache__' in str(py_file):
        continue
    
    content = py_file.read_text(encoding='utf-8')
    for pattern in old_patterns:
        if re.search(pattern, content):
            print(f"⚠️  {py_file}: Contains old import pattern")
```

## Recommended Fix Order

1. Fix `text_extraction/` files first (they're imported by other modules)
2. Fix `data_cleaning/` files
3. Fix `graph_extraction/` files
4. Fix `exam_generation/` files
5. Run tests to verify

## Temporary Workaround

If imports are causing issues, you can temporarily add to `sys.path`:

```python
import sys
from pathlib import Path

# Add old paths for compatibility
sys.path.insert(0, str(Path(__file__).parent.parent / "exam_analysis"))
sys.path.insert(0, str(Path(__file__).parent.parent))
```

But it's better to fix the imports properly!

