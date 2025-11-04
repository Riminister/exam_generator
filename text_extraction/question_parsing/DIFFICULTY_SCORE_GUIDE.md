# Difficulty Score Calculation Guide

## 🎯 How Difficulty Scores Are Calculated

Difficulty scores are now calculated based on **question marks** using the formula:

```
difficulty_score = question_marks / total_exam_marks
```

This gives you a normalized score between 0 and 1, where:
- **Higher scores** = More marks = Typically harder/more complex questions
- **Lower scores** = Fewer marks = Typically easier/simpler questions

## 📝 What We Extract

The calculator looks for marks in various formats:
- `(10pts)` or `(10 pts)` or `(10 points)` or `(10 marks)`
- `[10 MARKS]` or `[10 marks]`
- `10pts.` or `10 points`
- `(10)` - standalone number in parentheses
- `worth 10 points`
- `10 points each`

## ✅ Results

After running the calculator on your data:

- **11 exams** had marks found (85%)
- **2 exams** had no marks (ECON435, ELEC292)
- **79 questions** got difficulty scores calculated
- **122 questions** couldn't get scores (marks not found in text)

## 🔧 How to Use

### Option 1: Run the Calculator Script
```bash
python calculate_difficulty.py
```

This will:
1. Read `data/exam_analysis.json`
2. Extract marks from each question
3. Calculate total marks per exam
4. Calculate difficulty_score for each question
5. Save updated data back to `data/exam_analysis.json`

### Option 2: Use in Your Code
```python
from exam_analysis.difficulty_calculator import DifficultyCalculator, calculate_difficulty_from_marks

# Calculate for entire file
stats = calculate_difficulty_from_marks("data/exam_analysis.json")

# Or use the class directly
calculator = DifficultyCalculator()
marks = calculator.extract_question_marks("Question text (10pts)")
difficulty = calculator.calculate_difficulty_score(marks, 100)  # 10/100 = 0.1
```

## 📊 Understanding the Results

### Questions WITH Difficulty Scores
- **Score is between 0 and 1**
- Example: Question worth 10 points out of 100 total = 0.1
- Example: Question worth 25 points out of 100 total = 0.25

### Questions WITHOUT Difficulty Scores
- **difficulty_score will be `null` (None in Python)**
- This happens when:
  - Marks aren't found in the question text
  - No questions in the exam had marks (can't calculate total)
  - Marks are in a format we don't recognize

## ⚠️ Notes

1. **Total marks calculation**: We sum all question marks found in an exam. If only some questions have marks, the total might be incomplete.

2. **ECON370 had 2043 total marks** - This seems unusually high! Likely there was a mark extraction error (maybe extracted a year or page number). You may want to review this exam.

3. **Missing marks**: If marks aren't found, the question keeps `difficulty_score = null`. This is intentional - we don't want to guess!

4. **After calculating**: Run the data cleaner again to ensure cleaned data has the updated scores:
   ```bash
   python exam_analysis/run_cleaning.py
   ```

## 🔍 Verifying Results

Check your updated `data/exam_analysis.json`:

```json
{
  "questions": [
    {
      "text": "Question (10pts)",
      "difficulty_score": 0.1,  // 10/100 = 0.1
      "question_marks": 10       // Raw marks also saved
    },
    {
      "text": "Question without marks",
      "difficulty_score": null   // Unavailable
    }
  ]
}
```

## 🎯 Next Steps

1. ✅ **Review the results** - Check if marks were extracted correctly
2. ✅ **Run data cleaning** - `python exam_analysis/run_cleaning.py`
3. ✅ **Build models** - Use difficulty scores as features or targets
4. ✅ **Filter nulls** - When building difficulty models, filter out `None` values

## 💡 Tips

- **For ML models**: Filter questions where `difficulty_score is not None` before training
- **For analysis**: Questions with `null` scores still have other useful features (type, length, etc.)
- **Improve extraction**: If marks aren't found, check the question text format and add new patterns to `difficulty_calculator.py`

