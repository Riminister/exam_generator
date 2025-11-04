# 🔍 Why Your R² Score is Low (0.308) - Main Causes

## 📊 Current Situation

- **R² Score: 0.308** (31% variance explained)
- **RMSE: 0.175** (on 0-1 scale)
- **Data: 105 questions with scores** out of 294 total (35.7% have scores)

## 🔴 Main Causes

### **1. Sparse Data (BIGGEST ISSUE)**
**Problem:**
- Only **105/294 questions** (35.7%) have difficulty scores
- Model can only learn from 105 examples
- Too little data for a regression model

**Why this matters:**
- R² needs sufficient data points to learn patterns
- With <150 samples, model struggles to generalize
- You're losing 64% of your data!

**Solution:**
```python
# Check which exams have marks
# Many exams have no marks extracted
# Need to improve mark extraction patterns
```

### **2. Marks ≠ Difficulty (Conceptual Problem)**
**Problem:**
- Your difficulty score = `question_marks / total_exam_marks`
- **Higher marks ≠ Harder questions!**
- A 20pt question might be easier than a 5pt question
- Example: "List 5 reasons" (20pts) vs "Prove this theorem" (5pts)

**Why this matters:**
- You're predicting marks allocation, not actual difficulty
- Marks often reflect question length/complexity, not difficulty
- Model learns wrong signal

**Solution:**
- Need different difficulty signal:
  - Use question type (essay vs multiple choice)
  - Use question keywords ("prove" vs "list")
  - Use question length + complexity
  - **OR**: Manually label some questions as easy/medium/hard

### **3. Weak Features**
**Current features:**
- TF-IDF (bag of words)
- Basic counts (char_count, word_count)
- Simple keywords (has_explain, has_calculate)

**Why this matters:**
- These features don't capture question complexity
- Can't distinguish "easy 20pt question" from "hard 5pt question"
- Need semantic/structural features

**Better features needed:**
- Question type (essay questions are typically harder)
- Question structure (sub-questions, multi-part)
- Language complexity (vocabulary level)
- Cognitive level (remember vs analyze vs create)

### **4. Different Exam Contexts**
**Problem:**
- Questions from different exams normalized differently
- ECON exam might have different mark allocation than MATH exam
- Normalizing by exam total marks mixes contexts

**Why this matters:**
- A 0.1 score from ECON exam ≠ 0.1 from MATH exam
- Model tries to learn patterns across incompatible contexts

### **5. Low Variance in Target**
**Problem:**
- Difficulty scores clustered: Mean=0.152, many values ~0.05-0.25
- Limited range makes it hard to predict differences

**Why this matters:**
- If all values are similar, R² will be low
- Need more spread in difficulty scores

## ✅ Solutions (Priority Order)

### **Priority 1: Get More Data with Scores**
```bash
# Check which exams are missing marks
python -c "import json; data = json.load(open('data/exam_analysis.json')); 
[print(f'{e[\"filename\"]}: {sum(1 for q in e[\"questions\"] if q.get(\"question_marks\"))} questions with marks') 
for e in data['exams']]"
```

**Improve mark extraction patterns** - Add more regex patterns to find marks in different formats.

### **Priority 2: Redefine Difficulty Signal**

**Option A: Multi-factor difficulty**
```python
difficulty = f(
    question_type,      # essay = harder
    marks,              # more marks = more complex
    length,             # longer = more complex
    keywords,          # "prove" > "list"
    sub_questions       # has sub-questions = harder
)
```

**Option B: Manual labels**
- Label 50-100 questions as: easy (0.0-0.33), medium (0.34-0.66), hard (0.67-1.0)
- Use these for training

**Option C: Use question type as proxy**
```python
# Essay questions = 0.7-1.0 (hard)
# Numerical = 0.4-0.6 (medium)
# Multiple choice = 0.1-0.3 (easy)
# Short answer = 0.2-0.5 (easy-medium)
```

### **Priority 3: Better Features**
```python
# Add semantic features
features = [
    'is_essay',              # Essay questions are harder
    'has_prove_keywords',    # "prove", "show", "demonstrate"
    'has_list_keywords',     # "list", "name", "identify" (easier)
    'num_sub_questions',     # More sub-questions = harder
    'vocabulary_complexity',  # Advanced vocabulary
    'requires_calculation',  # Math questions
    'question_depth'         # Surface vs deep thinking
]
```

### **Priority 4: Separate by Exam Type**
Train separate models for:
- Math/Engineering exams
- Social Science exams  
- Language exams

## 🎯 Quick Wins

1. **Filter to questions WITH scores** (105 questions):
   ```python
   df_valid = df[df['difficulty_score'] > 0].copy()
   # This should already be done, but verify
   ```

2. **Add question_type as feature**:
   ```python
   df['is_essay'] = (df['question_type'] == 'essay').astype(int)
   df['is_multiple_choice'] = (df['question_type'] == 'multiple_choice').astype(int)
   ```

3. **Normalize features properly**:
   ```python
   # Already using StandardScaler - good!
   # But make sure you're scaling all features
   ```

## 📈 Expected Improvements

**If you fix:**
- **+50% more data** (105 → 157): R² might go to **0.35-0.40**
- **Better features** (question_type, complexity): R² might go to **0.45-0.55**
- **Redefine difficulty** (multi-factor): R² might go to **0.60-0.70**

## 🚀 Next Steps

1. **Run this to see which exams have marks:**
   ```bash
   python check_mark_coverage.py  # (I'll create this)
   ```

2. **Try redefining difficulty** using question type:
   ```python
   # In build_first_model.py
   df['difficulty_by_type'] = df['question_type'].map({
       'essay': 0.75,
       'numerical': 0.50,
       'short_answer': 0.35,
       'multiple_choice': 0.20,
       'true_false': 0.15,
       'other': 0.40
   })
   ```

3. **Improve mark extraction** to get more scores

---

**Bottom line:** Your R² is low because:
1. ⚠️ **Only 35% of data has scores** (sparse data)
2. ⚠️ **Marks ≠ difficulty** (wrong signal)
3. ⚠️ **Features don't capture complexity** (weak features)

**Best quick fix:** Redefine difficulty using question type + marks + length, not just marks/total.

