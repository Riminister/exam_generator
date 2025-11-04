# Data Cleaning Guide for Exam Bank Data

This guide explains how to clean your exam data to prepare it for machine learning model training and future exam generation.

## 🎯 Overview

The data cleaning pipeline removes noise, normalizes text, validates questions, and structures your exam data for optimal ML training. Clean data improves model performance and ensures high-quality exam generation.

## 📋 Prerequisites

1. **Run Initial Analysis**: First, you need to extract data from your PDFs using `phase1_starter.py`:
   ```bash
   python phase1_starter.py
   ```
   This creates `exam_analysis.json` with raw extracted questions.

2. **Install Dependencies**: Make sure you have all required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Simple Usage (Recommended)

Run the cleaning pipeline with default settings:

```bash
python exam_analysis/data_cleaner.py
```

This will:
- Load questions from `exam_analysis.json`
- Clean and validate all questions
- Remove duplicates and noise
- Save cleaned data to `exam_analysis/cleaned_questions.json`
- Export to CSV at `exam_analysis/cleaned_questions.csv`

### Option 2: Programmatic Usage

Use the cleaner in your own scripts:

```python
from exam_analysis.data_cleaner import ExamDataCleaner, clean_exam_data
import json

# Load your raw data
with open('exam_analysis.json', 'r') as f:
    data = json.load(f)

# Initialize cleaner with custom settings
cleaner = ExamDataCleaner(
    min_question_length=50,  # Minimum characters for a valid question
    min_answer_length=10      # Minimum characters for an answer
)

# Clean the questions
cleaned_questions = cleaner.clean_dataset(data['questions'])

# Get cleaning statistics
report = cleaner.generate_cleaning_report()
print(report)

# Save cleaned data
cleaner.save_cleaned_data(cleaned_questions, 'my_cleaned_data.json')
cleaner.export_to_csv(cleaned_questions, 'my_cleaned_data.csv')
```

## 🧹 What Gets Cleaned?

The cleaning pipeline performs these operations:

### 1. **Text Normalization**
- Removes excessive whitespace
- Fixes encoding issues (BOM, zero-width spaces)
- Normalizes quotes and dashes
- Standardizes formatting

### 2. **Noise Removal**
Removes common noise patterns:
- Page numbers ("Page 1 of 5")
- Dates and copyright notices
- Headers/footers (university names, course codes)
- URLs and email addresses
- Instructions repeated on every page

### 3. **Question Validation**
Validates each question:
- ✅ Minimum length requirement (default: 30 characters)
- ✅ Actual content (not just punctuation)
- ✅ Not a header/footer fragment
- ✅ Contains meaningful text

### 4. **Duplicate Removal**
- Identifies exact duplicates using hashing
- Removes similar questions (85% similarity threshold)
- Preserves unique questions only

### 5. **Structure Enhancement**
- Extracts multiple choice options
- Categorizes question types
- Maintains metadata (topics, difficulty scores)
- Creates consistent data structure

## 📊 Understanding the Output

### JSON Format

The cleaned JSON file contains:

```json
{
  "cleaned_questions": [
    {
      "id": 1,
      "text": "What is the primary purpose of market research?",
      "question_type": "multiple_choice",
      "options": [
        "To increase sales",
        "To understand customer needs",
        "To reduce costs",
        "To improve product quality"
      ],
      "num_options": 4,
      "difficulty_score": 1.5,
      "topics": ["business", "marketing"],
      "text_length": 280,
      "original_length": 320
    }
  ],
  "cleaning_stats": {
    "total_questions": 150,
    "removed_duplicates": 5,
    "removed_too_short": 8,
    "removed_invalid": 2,
    "final_count": 135,
    "retention_rate": "90.0%"
  }
}
```

### CSV Format

The CSV file is optimized for data analysis and ML model training:

| id | text | question_type | difficulty_score | topics | text_length | num_options |
|----|------|---------------|------------------|--------|-------------|-------------|
| 1 | What is... | multiple_choice | 1.5 | business, marketing | 280 | 4 |

## ⚙️ Configuration Options

### Adjust Minimum Lengths

For shorter/longer questions:

```python
cleaner = ExamDataCleaner(
    min_question_length=50,  # Increase for longer questions
    min_answer_length=15     # Increase for detailed answers
)
```

### Adjust Similarity Threshold

For stricter/looser duplicate detection:

```python
cleaned = cleaner.remove_duplicates(
    questions,
    similarity_threshold=0.90  # Higher = stricter (0.85 default)
)
```

## 📈 Cleaning Statistics

After cleaning, you'll see a report like:

```
============================================================
CLEANING REPORT
============================================================
Total questions processed: 150
Removed duplicates: 5
Removed (too short): 8
Removed (invalid): 2
Final count: 135
Retention rate: 90.0%
============================================================
```

**What these numbers mean:**
- **Total questions**: Raw questions from PDF extraction
- **Removed duplicates**: Exact or highly similar questions removed
- **Removed (too short)**: Questions below minimum length threshold
- **Removed (invalid)**: Questions that don't meet quality criteria
- **Final count**: Questions ready for ML training
- **Retention rate**: Percentage of questions kept

## 🔍 Quality Control

### Before Cleaning
- Review a sample of raw questions
- Identify common patterns in noisy data
- Adjust cleaning parameters if needed

### After Cleaning
1. **Spot Check**: Review random cleaned questions
2. **Verify**: Ensure important content isn't removed
3. **Analyze**: Check statistics for anomalies
4. **Iterate**: Adjust parameters and re-clean if needed

### Common Issues and Fixes

| Issue | Symptom | Solution |
|-------|---------|----------|
| Too many questions removed | Low retention rate | Lower `min_question_length` |
| Duplicates still present | High similarity questions | Increase `similarity_threshold` |
| Important text removed | Missing context | Adjust noise patterns |
| Invalid questions kept | Poor quality data | Increase validation checks |

## 🔄 Workflow Integration

### Complete Pipeline

```bash
# Step 1: Extract data from PDFs
python phase1_starter.py

# Step 2: Clean the extracted data
python exam_analysis/data_cleaner.py

# Step 3: Use cleaned data for ML training
# (Your ML training scripts can now load cleaned_questions.json)
```

### Integration with ML Pipeline

```python
import json
import pandas as pd

# Load cleaned data
with open('exam_analysis/cleaned_questions.json', 'r') as f:
    data = json.load(f)

questions = data['cleaned_questions']

# Convert to DataFrame for ML training
df = pd.DataFrame([
    {
        'text': q['text'],
        'type': q['question_type'],
        'difficulty': q['difficulty_score']
    }
    for q in questions
])

# Now ready for tokenization, embedding, model training, etc.
```

## 📁 File Structure

After running the cleaning pipeline:

```
exam_analysis/
├── data_cleaner.py              # Cleaning module
├── cleaned_questions.json       # Cleaned data (JSON)
├── cleaned_questions.csv        # Cleaned data (CSV)
└── DATA_CLEANING_GUIDE.md       # This guide
```

## 🎓 Best Practices

1. **Always Backup**: Keep your raw `exam_analysis.json` file
2. **Review Results**: Spot-check cleaned questions before ML training
3. **Iterate**: Adjust parameters based on your specific exam types
4. **Document Changes**: Note any custom cleaning rules you add
5. **Version Control**: Track different cleaning configurations

## 🐛 Troubleshooting

### Error: "Input file not found"
- Make sure you've run `phase1_starter.py` first
- Check that `exam_analysis.json` exists in the root directory

### Too Many Questions Removed
- Lower the `min_question_length` threshold
- Review noise patterns to ensure they're not too aggressive

### Duplicates Not Detected
- Increase the `similarity_threshold` value
- Check if questions are actually duplicates or just similar

### Memory Issues with Large Datasets
- Process in batches
- Use generator functions for memory efficiency

## 🔜 Next Steps

After cleaning your data:

1. **Visualize**: Create plots to understand question distribution
2. **Analyze**: Study patterns in question types and topics
3. **Train Models**: Use cleaned data for NLP model training
4. **Generate Exams**: Create new questions based on cleaned patterns

## 📚 Additional Resources

- See `phase1_starter.py` for initial data extraction
- Check `IMPLEMENTATION_ROADMAP.md` for overall project structure
- Review `PROJECT_GOALS.md` for project objectives

---

**Ready to clean your exam data? Run:**

```bash
python exam_analysis/data_cleaner.py
```

Happy cleaning! 🧹✨

