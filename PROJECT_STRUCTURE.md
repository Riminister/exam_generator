# 📁 Project Structure

## Current Organization

```
Parse_Files/
├── data/                          # Data files
│   ├── exam_analysis.json         # Parsed questions
│   ├── extracted_text.json        # Raw extracted text
│   └── exam_downloads/            # PDF files
│       ├── to_process/           # PDFs to process
│       └── processed/            # Processed PDFs
│
├── exam_analysis/                 # Core analysis modules
│   ├── data_cleaner.py           # Data cleaning pipeline
│   ├── question_type_detector.py # Question type detection
│   ├── difficulty_calculator.py  # Difficulty scoring
│   ├── cover_page_parser.py      # Cover page extraction
│   ├── text_extractor.py         # Text extraction
│   ├── graph_analyzer.py         # Graph analysis (OpenAI)
│   ├── graph_recreator.py        # Graph recreation (matplotlib)
│   └── openai_question_analyzer.py # OpenAI question analysis
│
├── models/                        # ML models
│   ├── build_first_model.py      # Starter model
│   ├── build_improved_difficulty_model.py
│   └── analyze_course_strategy.py
│
├── scripts/                       # Utility scripts
│   ├── setup_openai.py           # OpenAI setup
│   ├── generate_exam_from_data.py # Exam assembly
│   ├── integrate_openai_analysis.py
│   └── organize_project.py       # Project organization
│
├── tests/                         # Test suite
│   └── test_comprehensive.py     # Comprehensive tests
│
├── outputs/                       # Generated outputs
│   └── generated_graphs/          # Recreated graphs
│
├── docs/                          # Documentation
│   ├── guides/                   # How-to guides
│   ├── PROJECT_GOALS.md
│   └── IMPLEMENTATION_ROADMAP.md
│
├── notebooks/                     # Jupyter notebooks
│   └── exploratory_analysis.ipynb
│
├── extract_text_from_pdfs.py      # Main: Extract text
├── parse_questions_from_text.py   # Main: Parse questions
├── openai_question_generator.py   # Main: Generate questions
│
├── requirements.txt               # Dependencies
└── README.md                      # Main documentation
```

## File Categories

### Core Pipeline (Root Level)
- `extract_text_from_pdfs.py` - Extract text from PDFs
- `parse_questions_from_text.py` - Parse questions from text
- `openai_question_generator.py` - Generate new questions

### Analysis Modules (`exam_analysis/`)
- Data processing and cleaning
- Question type detection
- Difficulty calculation
- Graph analysis and recreation

### ML Models (`models/`)
- Model building scripts
- Model analysis tools

### Utility Scripts (`scripts/`)
- Setup and configuration
- Integration scripts
- Utility tools

### Tests (`tests/`)
- Comprehensive test suite
- Component tests

### Documentation (`docs/`)
- Project documentation
- How-to guides
- Implementation guides

## Running Tests

```bash
# Run comprehensive test suite
python tests/test_comprehensive.py
```

## Organizing Project

```bash
# Preview changes
python scripts/organize_project.py --dry-run

# Execute organization
python scripts/organize_project.py
```

