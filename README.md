# AI-Powered Exam Generation System

An intelligent system that analyzes exam bank data and generates new exam questions using machine learning.

## 🎯 Project Status

**Current Phase**: Model Building & Analysis

You have successfully extracted and organized exam data. The project is now focused on building machine learning models to understand exam patterns and generate new questions.

## 📁 Project Structure

```
Parse_Files/
├── data/                      # Data files
│   ├── exam_analysis.json     # Extracted exam questions (201 questions from 13 exams)
│   └── exam_downloads/        # Original PDF files
│
├── models/                    # Machine Learning Models
│   ├── README.md             # Model building guide
│   ├── build_first_model.py  # Starter script for first ML model
│   └── check_current_data.py # Dataset analysis tool
│
├── exam_analysis/            # Data Processing & Cleaning
│   ├── enhanced_extractor.py # PDF text extraction with OCR support
│   ├── data_cleaner.py       # Data cleaning pipeline
│   ├── run_cleaning.py       # Run data cleaning
│   └── DATA_CLEANING_GUIDE.md
│
├── docs/                     # Documentation
│   ├── PROJECT_GOALS.md      # Project objectives and vision
│   ├── IMPLEMENTATION_ROADMAP.md  # Step-by-step implementation guide
│   └── PROJECT_STRUCTURE.md  # Technical structure
│
├── queens_exam_env/          # Python virtual environment
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### 0. Extract Cover Page Metadata (New!)
```bash
python extract_cover_page_metadata.py
```
Extracts metadata from exam cover pages: faculty, professor, course name, total marks, and dates.
Automatically detects OCR settings needed for each exam type (language, math, etc.).
See `docs/COVER_PAGE_EXTRACTION_GUIDE.md` for details.

### 1. Calculate Difficulty Scores
```bash
python calculate_difficulty.py
```
Calculates difficulty scores based on question marks: `difficulty_score = question_marks / total_exam_marks`
Now prefers total marks from cover page (more accurate)!
See `DIFFICULTY_SCORE_GUIDE.md` for details.

### 2. Detect Sub-Questions (New!)
```bash
python detect_sub_questions.py
```
Detects sub-questions (a), i., ii.) that follow numbered questions.
See `SUB_QUESTION_GUIDE.md` for details.

### 3. Detect Translation & OCR Issues (New!)
```bash
python detect_translation_issues.py
```
Identifies translation questions with poor OCR quality (especially Arabic).
Marks questions that need re-extraction with proper language support.
See `OCR_RE_EXTRACTION_GUIDE.md` for fixing instructions.

### 4. Explore Your Data (Recommended!)
```bash
# Open the exploratory analysis notebook
jupyter notebook notebooks/exploratory_analysis.ipynb
# OR open it directly in VS Code/PyCharm
```
This comprehensive notebook helps you understand your data before building models.
See `notebooks/HOW_TO_USE_EDA.md` for a detailed guide.

### 5. Check Your Data (Quick Overview)
```bash
python models/check_current_data.py
```
This shows a quick summary of your dataset.

### 6. Clean Your Data (Recommended)
```bash
python exam_analysis/run_cleaning.py
```
Prepares data for machine learning by removing noise and duplicates.

### 7. Build Your First Model
```bash
python models/build_first_model.py
```
Trains initial models for:
- Question type classification
- Difficulty prediction

### 8. Read the Model Building Guide
See `models/README.md` (formerly MODEL_BUILDING_GUIDE.md) for:
- Step-by-step model building process
- When to download more exams
- Advanced techniques
- Best practices

## 📊 Current Dataset

- **13 exams** from various courses
- **201 questions** extracted and analyzed
- **Question types**: Essay (25%), Short Answer (19%), Numerical (8%), True/False (7%), Other (41%)
- **Courses**: ARAB100, ECON310-435, ELEC252-372

## 🎯 Next Steps

1. **Explore your data** - Run the EDA notebook to understand what you have
2. **Clean your data** - Run the cleaning pipeline to prepare for ML
3. **Build first models** - Start with simple classification
4. **Evaluate results** - See what works and what doesn't
5. **Iterate** - Improve models based on results
6. **Then scale up** - Download more exams if needed

**Detailed Workflow**:
```
1. Run EDA notebook → Understand your data
2. Run data cleaning → Remove noise and duplicates  
3. Build first model → Test your approach
4. Evaluate → Identify improvements
5. Iterate → Improve models
6. Scale up → Download more data if needed
```

## 📚 Documentation

- **`docs/TEXT_EXTRACTION_GUIDE.md`** - **NEW!** How to extract words/text from PDFs
- **`docs/COVER_PAGE_EXTRACTION_GUIDE.md`** - Cover page metadata extraction & context-based OCR
- **`FEATURES_SUMMARY.md`** - Overview of difficulty scores and sub-question detection
- **`DIFFICULTY_SCORE_GUIDE.md`** - How difficulty scores are calculated
- **`SUB_QUESTION_GUIDE.md`** - How sub-questions are detected
- **`OCR_RE_EXTRACTION_GUIDE.md`** - How to fix Arabic/translation OCR issues
- **`notebooks/HOW_TO_USE_EDA.md`** - Step-by-step guide to exploratory analysis
- **`models/README.md`** - Complete guide to building ML models
- **`docs/PROJECT_GOALS.md`** - Project vision and objectives
- **`docs/IMPLEMENTATION_ROADMAP.md`** - Detailed implementation steps
- **`exam_analysis/DATA_CLEANING_GUIDE.md`** - Data cleaning guide

## 🛠️ Requirements

- Python 3.9+
- See `requirements.txt` for all dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

Key ML packages:
- scikit-learn (classification, regression)
- pandas (data manipulation)
- numpy (numerical operations)
- transformers (optional, for advanced NLP)

## 📝 Workflow

```
1. Data Extraction (DONE ✅)
   └── exam_analysis.json created

2. Extract Cover Page Metadata (NEW! ✅)
   └── Run: python extract_cover_page_metadata.py
   └── Extracts: faculty, professor, dates, total marks, OCR config

3. Data Cleaning
   └── Run: python exam_analysis/run_cleaning.py
   └── Output: exam_analysis_cleaned.json

4. Calculate Difficulty Scores
   └── Run: python calculate_difficulty.py
   └── Uses cover page total marks (more accurate!)

5. Model Building (CURRENT FOCUS)
   └── Start: python models/build_first_model.py
   └── Iterate based on results

6. Model Evaluation
   └── Analyze accuracy, identify improvements

7. Scale Up (Future)
   └── Download more exams if models work well
```

## 💡 Key Decisions Made

- ✅ **Parsing/download code removed** - Focus on model building
- ✅ **Data organized** - Clean structure for ML workflow
- ✅ **Model building ready** - Starter scripts and guides provided

## 🆘 Getting Help

1. **Check the guide**: `models/README.md` has detailed explanations
2. **Review your data**: Run `models/check_current_data.py` to see what you have
3. **Start simple**: Use `models/build_first_model.py` as a starting point

## 📄 License

MIT License

---

**Ready to build ML models! 🚀**

**Recommended Start**: 
1. Run exploratory analysis: `jupyter notebook notebooks/exploratory_analysis.ipynb`
2. Read the guide: `notebooks/HOW_TO_USE_EDA.md`
3. Then proceed with data cleaning and model building
