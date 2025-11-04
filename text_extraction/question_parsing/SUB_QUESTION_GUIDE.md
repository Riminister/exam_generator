# Sub-Question Detection Guide

## 🎯 What Are Sub-Questions?

Sub-questions are parts of a larger question. For example:

**Main Question:**
```
7. From the same text, extract the words that represent the following terms:
```

**Sub-Questions:**
```
i. Four Noun Adjective Phrase: 2 definite and 2 indefinites.
ii. An iDaafa Phrase
iii. A Verb in the Past Progressive
```

## 🔍 How Detection Works

Sub-questions are detected when:
1. **Question text starts with** a letter or roman numeral marker:
   - `a)`, `b)`, `c)` 
   - `(a)`, `(b)`, `(c)`
   - `a.`, `b.`, `c.`
   - `i.`, `ii.`, `iii.`, `iv.`, etc.
   - `(i)`, `(ii)`, `(iii)`, etc.

2. **Previous question starts with** a number:
   - `1.`, `2.`, `7.`, etc.
   - `Question 1`, `Question 2`
   - `Q1.`, `Q2.`

3. **Result**: Question type is set to `'sub_question'`

## ✅ Results from Your Data

After running detection:
- **25 sub-questions** detected across all exams
- **ARAB100.pdf**: 23 sub-questions (41.1% of questions!)
- **ELEC333.pdf**: 2 sub-questions
- Most exams: 0 sub-questions (questions are properly numbered)

## 📊 What Gets Added

Each sub-question gets:
- `question_type`: Changed to `'sub_question'`
- `is_sub_question`: Set to `true`
- `parent_question_number`: Reference to the parent question

## 🔧 How to Use

### Option 1: Run Detection Script
```bash
python detect_sub_questions.py
```

### Option 2: Use in Code
```python
from exam_analysis.sub_question_detector import SubQuestionDetector

detector = SubQuestionDetector()
updated_questions = detector.detect_sub_questions(questions)
stats = detector.get_sub_question_stats(updated_questions)
```

## 💡 Use Cases

### Filter Sub-Questions Out
```python
# When analyzing, you might want only main questions
main_questions = [q for q in questions if q['question_type'] != 'sub_question']
```

### Group with Parent
```python
# Group sub-questions with their parent
parent_to_subs = {}
for q in questions:
    if q['question_type'] == 'sub_question':
        parent = q.get('parent_question_number')
        if parent not in parent_to_subs:
            parent_to_subs[parent] = []
        parent_to_subs[parent].append(q)
```

### Include in Analysis
```python
# Analyze both main and sub-questions separately
sub_questions = [q for q in questions if q['question_type'] == 'sub_question']
main_questions = [q for q in questions if q['question_type'] != 'sub_question']
```

## 📝 Example Data Structure

```json
{
  "question_number": 2,
  "text": "7. Extract the following terms:",
  "question_type": "other"
},
{
  "question_number": 3,
  "text": "i. Four Noun Adjective Phrase",
  "question_type": "sub_question",
  "is_sub_question": true,
  "parent_question_number": 2
}
```

## 🎯 Next Steps

1. ✅ **Review results**: Check if sub-questions are correctly identified
2. ✅ **Run data cleaning**: `python exam_analysis/run_cleaning.py` (preserves sub_question types)
3. ✅ **Build models**: Decide whether to include/exclude sub-questions
4. ✅ **Analysis**: Sub-questions can provide more granular insights

## ⚠️ Notes

- Sub-questions follow the **previous question** in sequence
- If multiple sub-questions exist (i., ii., iii.), they all link to the same parent
- First question in a list can't be a sub-question (no previous question)
- Sub-questions keep their original metadata (difficulty, topics, etc.)

