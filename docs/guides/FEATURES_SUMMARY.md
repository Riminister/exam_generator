# Features Summary: Difficulty Scores & Sub-Questions

## ✅ Implemented Features

### 1. **Difficulty Score Calculation from Marks**

**How it works:**
- Extracts marks from question text (e.g., `(10pts)`, `10 points`, `[10 MARKS]`)
- Calculates total exam marks (sum of all question marks)
- Computes: `difficulty_score = question_marks / total_exam_marks`
- Sets `difficulty_score = null` if marks not found

**Error Handling:**
- ✅ **If total marks > 300**: Automatically sets to `null` (likely extraction error)
- Example: ECON370 had 2043 marks → automatically corrected to `null`

**Results:**
- 75 questions got difficulty scores calculated
- 122 questions couldn't get scores (marks not found)
- 10 exams had marks successfully extracted

**Files:**
- `exam_analysis/difficulty_calculator.py` - Core calculation logic
- `calculate_difficulty.py` - Run this to calculate scores

---

### 2. **Sub-Question Detection**

**How it works:**
- Detects when questions start with letter/roman numeral markers (`a)`, `i.`, `ii.`, etc.)
- Checks if previous question starts with a number (`1.`, `2.`, `7.`, etc.)
- Marks as `question_type = 'sub_question'`
- Links to parent question via `parent_question_number`

**Patterns Detected:**
- Letters: `a)`, `b)`, `(a)`, `a.`
- Roman numerals: `i.`, `ii.`, `iii.`, `iv.`, `(i)`, `(ii)`

**Results:**
- 25 sub-questions detected
- ARAB100.pdf: 23 sub-questions (41.1% of questions!)
- ELEC333.pdf: 2 sub-questions

**Files:**
- `exam_analysis/sub_question_detector.py` - Detection logic
- `detect_sub_questions.py` - Run this to detect sub-questions

---

## 🔄 Complete Workflow

### Step 1: Calculate Difficulty Scores
```bash
python calculate_difficulty.py
```
- Extracts marks from questions
- Calculates difficulty scores
- Validates totals (rejects >300)

### Step 2: Detect Sub-Questions
```bash
python detect_sub_questions.py
```
- Identifies sub-questions
- Links to parent questions
- Marks question_type = 'sub_question'

### Step 3: Clean Data
```bash
python exam_analysis/run_cleaning.py
```
- Preserves difficulty scores (including null values)
- Preserves sub_question types
- Removes duplicates and noise

---

## 📊 Example Output

### Question with Difficulty Score
```json
{
  "question_number": 1,
  "text": "Question (10pts)",
  "difficulty_score": 0.1,  // 10/100 = 0.1
  "question_marks": 10.0,
  "question_type": "essay"
}
```

### Question without Marks
```json
{
  "question_number": 2,
  "text": "Question without marks",
  "difficulty_score": null,  // Unavailable
  "question_marks": null,
  "question_type": "other"
}
```

### Sub-Question
```json
{
  "question_number": 3,
  "text": "i. Four Noun Adjective Phrase",
  "question_type": "sub_question",
  "is_sub_question": true,
  "parent_question_number": 2,
  "difficulty_score": null
}
```

---

## 🎯 Usage in Models

### Filter Questions with Scores
```python
# Only use questions with calculated difficulty scores
df_with_scores = df[df['difficulty_score'].notna()]

# Filter out sub-questions if desired
main_questions = df[df['question_type'] != 'sub_question']
```

### Handle Sub-Questions
```python
# Option 1: Exclude sub-questions
main_only = df[df['question_type'] != 'sub_question']

# Option 2: Include but mark
df['is_sub'] = df['question_type'] == 'sub_question'

# Option 3: Group with parent
parent_groups = df.groupby('parent_question_number')
```

---

## 📝 Next Steps

1. ✅ **Calculate difficulty scores** - Already done!
2. ✅ **Detect sub-questions** - Already done!
3. ✅ **Run data cleaning** - Preserves both features
4. ✅ **Build models** - Use difficulty scores and sub-question info

---

## 🔍 Verification

Check your `data/exam_analysis.json`:
- ✅ Questions with `(10pts)` → `difficulty_score: 0.1` (if total is 100)
- ✅ Questions without marks → `difficulty_score: null`
- ✅ Sub-questions → `question_type: "sub_question"` + `parent_question_number`
- ✅ ECON370 (2043 marks) → Automatically set to `null` ✅

All features are working! 🎉

