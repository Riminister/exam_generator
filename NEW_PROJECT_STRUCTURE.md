# 📁 New Project Structure

## Clean Organization

```
Parse_Files/
├── data/                              # Data files
│   ├── exam_analysis.json
│   ├── extracted_text.json
│   └── exam_downloads/
│
├── exam_generation/                   # ⭐ NEW: Exam generation
│   ├── openai/                       # OpenAI question generation
│   │   ├── openai_question_generator.py
│   │   ├── OPENAI_SETUP_GUIDE.md
│   │   └── OPENAI_GRAPH_INTEGRATION_GUIDE.md
│   └── assembly/                     # Exam assembly from existing questions
│       └── generate_exam_from_data.py
│
├── text_extraction/                   # ⭐ NEW: Text extraction
│   ├── pdf_processing/               # PDF extraction
│   │   ├── extract_text_from_pdfs.py
│   │   ├── extract_cover_page_metadata.py
│   │   ├── text_extractor.py
│   │   ├── cover_page_parser.py
│   │   └── ocr_context_selector.py
│   └── question_parsing/              # Question parsing
│       ├── parse_questions_from_text.py
│       ├── detect_question_types.py
│       ├── question_type_detector.py
│       ├── sub_question_detector.py
│       └── translation_detector.py
│
├── graph_extraction/                   # ⭐ NEW: Graph extraction
│   ├── analysis/                     # Graph analysis
│   │   ├── graph_analyzer.py
│   │   ├── openai_question_analyzer.py
│   │   └── integrate_openai_analysis.py
│   └── recreation/                    # Graph recreation
│       ├── graph_recreator.py
│       └── graph_generator.py
│
├── data_cleaning/                      # ⭐ NEW: Data cleaning
│   ├── cleaners/                     # Cleaning modules
│   │   └── data_cleaner.py
│   ├── validators/                    # Validation modules
│   │   ├── difficulty_calculator.py
│   │   └── calculate_difficulty.py
│   ├── run_cleaning.py
│   └── DATA_CLEANING_GUIDE.md
│
├── models/                             # ML models
│   ├── build_first_model.py
│   ├── build_improved_difficulty_model.py
│   └── analyze_course_strategy.py
│
├── scripts/                            # Utility scripts
│   ├── setup_openai.py
│   └── organize_project.py
│
├── tests/                              # Test suite
│   └── test_comprehensive.py
│
├── outputs/                            # Generated outputs
│   ├── generated_graphs/
│   ├── generated_exams/
│   └── analysis_results/
│
├── docs/                               # Documentation
│   ├── guides/                        # How-to guides
│   └── [project docs]
│
├── notebooks/                          # Jupyter notebooks
│   └── exploratory_analysis.ipynb
│
└── [root scripts]                      # Main entry points
    ├── extract_text_from_pdfs.py      # (or move to text_extraction/)
    ├── parse_questions_from_text.py   # (or move to text_extraction/)
    └── requirements.txt
```

## Key Changes

### 1. Exam Generation (`exam_generation/`)
- **OpenAI integration**: Question generation with AI
- **Exam assembly**: Create exams from existing questions

### 2. Text Extraction (`text_extraction/`)
- **PDF Processing**: Extract text from PDFs, OCR, cover pages
- **Question Parsing**: Parse and structure questions from text

### 3. Graph Extraction (`graph_extraction/`)
- **Analysis**: Analyze graphs/figures in questions (OpenAI)
- **Recreation**: Recreate graphs using matplotlib

### 4. Data Cleaning (`data_cleaning/`)
- **Cleaners**: Text cleaning, normalization
- **Validators**: Difficulty calculation, validation

## Benefits

✅ **Clear separation** of concerns
✅ **Easy to find** related files
✅ **Scalable** structure
✅ **Better organization** for team projects

## Migration Notes

After reorganization, update imports:

```python
# Old
from exam_analysis.data_cleaner import ExamDataCleaner

# New
from data_cleaning.cleaners.data_cleaner import ExamDataCleaner
```

See `REORGANIZATION_NOTES.md` for complete import update guide.

