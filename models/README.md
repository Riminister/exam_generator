# Model Building Guide: Start Here! 🚀

## 📊 Your Current Situation

You have:
- ✅ **13 exams** from different courses
- ✅ **201 questions** extracted and analyzed
- ✅ Mixed question types (essay, short_answer, numerical, true_false, other)
- ✅ Data in `exam_analysis.json`

## 🎯 My Recommendation: **START WITH WHAT YOU HAVE**

### Why Start Small First?

1. **Validate Your Pipeline** - Make sure data cleaning and preprocessing works correctly
2. **Test Model Approaches** - Try different ML techniques without wasting time
3. **Identify Issues Early** - Find data quality problems before scaling up
4. **Iterate Faster** - Quick feedback loops with smaller dataset
5. **Build Confidence** - See results before investing time in downloading 100s of exams

### When to Download More Exams?

Download more exams **AFTER** you've:
- ✅ Validated your data cleaning pipeline works
- ✅ Built and tested initial models successfully
- ✅ Understand what features/models work best
- ✅ Confirmed you need more data for better results

**Rule of thumb**: If your current models work well on 201 questions, they'll work even better with more data. If they don't work well, more data won't help—you need to fix the approach first.

---

## 📋 Step-by-Step Model Building Plan

### **Phase 1: Data Preparation (1-2 days)**

#### Step 1.1: Clean Your Data
```bash
# Run the data cleaner
python exam_analysis/run_cleaning.py
# or
python -m exam_analysis.data_cleaner
```

This will:
- Remove noise and duplicate questions
- Standardize question formats
- Extract multiple choice options properly
- Validate question quality

**Output**: `exam_analysis_cleaned.json`

#### Step 1.2: Explore Your Data
Create a Jupyter notebook to:
- Visualize question type distribution
- Analyze difficulty scores
- Check topic coverage
- Identify data quality issues

**Questions to answer**:
- Are questions properly classified?
- Is difficulty scoring working?
- Are topics being extracted correctly?

---

### **Phase 2: Start with Simple Models (3-5 days)**

#### Step 2.1: Question Type Classification ✅ **START HERE**

**Goal**: Predict question type (essay, multiple_choice, short_answer, etc.)

**Why start here**:
- Easier problem (classification)
- Can validate with your current data
- Useful feature for downstream models

**Approach**:
```python
# Simple approach: TF-IDF + Logistic Regression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# 1. Load cleaned data
# 2. Extract features (question text → TF-IDF vectors)
# 3. Train classifier
# 4. Evaluate (should get 70-85% accuracy)
```

**Expected Results**: 
- Accuracy: 70-85% (good enough to validate approach)
- If <60%: need better features or more data
- If >85%: ready to move to harder problems

#### Step 2.2: Difficulty Prediction

**Goal**: Predict difficulty score (0-1 scale) for questions

**Approach**:
```python
# Regression problem
from sklearn.ensemble import RandomForestRegressor

# Features:
# - Question length
# - Question type
# - Number of words
# - Presence of technical terms
# - Course code
```

**Expected Results**:
- R² score: 0.3-0.6 (decent for first attempt)
- RMSE: <0.3 (difficulty is on 0-1 scale)

#### Step 2.3: Topic Extraction/Classification

**Goal**: Automatically tag questions with topics

**Approach**:
```python
# Option 1: Simple keyword matching
# Option 2: LDA Topic Modeling
from sklearn.decomposition import LatentDirichletAllocation

# Option 3: Use pre-trained models (better!)
from transformers import pipeline

classifier = pipeline("zero-shot-classification", 
                     model="facebook/bart-large-mnli")
```

---

### **Phase 3: Evaluate & Iterate (2-3 days)**

#### Step 3.1: Create Evaluation Metrics

Build a script that:
- Splits data into train/validation/test sets
- Measures model performance
- Shows confusion matrices
- Provides actionable insights

#### Step 3.2: Fix Issues

Common problems:
- **Low accuracy**: Need better features (try BERT embeddings)
- **Overfitting**: Need more data or regularization
- **Class imbalance**: Use class weights or SMOTE
- **Data quality**: Clean data better

#### Step 3.3: Document What Works

Write down:
- Which models work best?
- What features are most important?
- What preprocessing steps are essential?
- What doesn't work?

---

### **Phase 4: Scale Up Decision Point** 🤔

#### If Models Work Well (Accuracy >70%):
✅ **Download more exams** to improve generalization
- Aim for 50-100 exams
- Prioritize courses with most questions
- Maintain class balance

#### If Models Struggle (Accuracy <60%):
⚠️ **Fix pipeline first** before downloading more
- Review data quality
- Try different features/models
- Consult with domain experts
- Consider using pre-trained models (BERT, GPT-embeddings)

---

## 🛠️ Practical Implementation Guide

### Quick Start: Build Your First Model

Create `build_first_model.py`:

```python
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# 1. Load data
with open('exam_analysis.json', 'r') as f:
    data = json.load(f)

# 2. Convert to DataFrame
questions = []
for exam in data['exams']:
    for q in exam['questions']:
        questions.append({
            'text': q['text'],
            'question_type': q['question_type'],
            'difficulty': q.get('difficulty_score', 0),
        })

df = pd.DataFrame(questions)

# 3. Prepare features
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X = vectorizer.fit_transform(df['text'])
y = df['question_type']

# 4. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 6. Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
```

Run this to get your first baseline!

---

## 📚 Recommended Learning Path

### Beginner → Intermediate
1. **Scikit-learn basics**: Classification, regression
2. **Text preprocessing**: Tokenization, stemming, TF-IDF
3. **Evaluation metrics**: Accuracy, precision, recall, F1

### Intermediate → Advanced
1. **Transformer models**: BERT, RoBERTa (via HuggingFace)
2. **Deep learning**: Neural networks for NLP
3. **Advanced NLP**: Named Entity Recognition, Topic Modeling

### Resources:
- **Scikit-learn docs**: https://scikit-learn.org/
- **HuggingFace**: https://huggingface.co/transformers/
- **Course**: Fast.ai Practical Deep Learning

---

## 🎯 Success Criteria

Your models are ready for more data when:

- ✅ Question type classification: >75% accuracy
- ✅ Data cleaning removes 80%+ of noise
- ✅ You understand which features matter
- ✅ Models generalize (work on unseen questions)
- ✅ You can explain model predictions

---

## 🚀 Next Steps Right Now

1. **Clean your data**:
   ```bash
   python exam_analysis/run_cleaning.py
   ```

2. **Run analysis**:
   ```bash
   python check_current_data.py
   ```

3. **Start building first model** (use code template above)

4. **Create evaluation script** to measure performance

5. **Document results** - keep track of what works!

---

## 💡 Pro Tips

1. **Start simple**: Logistic regression before deep learning
2. **Use pre-trained models**: Don't train from scratch (BERT, etc.)
3. **Feature engineering matters**: Better features > More data
4. **Validate properly**: Use train/validation/test splits
5. **Iterate quickly**: Test ideas fast, then invest in best approaches

---

## ❓ FAQ

**Q: How many questions do I need?**
A: For classification: 100+ per class. You have ~200 total, so you're at the minimum. Start with what you have!

**Q: Should I download all exams first?**
A: No! Test with 13 exams first. If models work, download more. If they don't, fix pipeline first.

**Q: What if my models don't work?**
A: Try:
- Better preprocessing
- More features (BERT embeddings)
- Pre-trained models
- Domain-specific techniques

**Q: How do I know if I need more data?**
A: If accuracy plateaus after adding more data, you need better models/features, not more data.

---

## 📞 When to Get Help

- Can't get >50% accuracy → Review data quality
- Models overfit badly → Need regularization or more data
- Don't understand results → Review ML basics
- Want to use advanced models → Learn transformers/BERT first

Good luck! Start with the simple model above and iterate from there. 🎉

