# 🚀 Complete Guide: Building Your First ML Model

## 📋 Prerequisites Checklist

Before building your model, ensure you have:

- [x] ✅ Python environment activated (`queens_exam_env`)
- [x] ✅ All PDFs extracted (21 exams in `extracted_text.json`)
- [ ] ⚠️  `exam_analysis.json` with parsed questions (currently has 13, needs 21)
- [ ] ⚠️  Required ML packages installed
- [ ] ⚠️  Data cleaned and prepared

---

## 🎯 Step-by-Step Process

### Step 1: Verify Your Data

Check what you currently have:

```bash
python models/check_current_data.py
```

This will show:
- How many exams you have
- How many questions per exam
- Question type distribution
- Recommendations

### Step 2: Install ML Dependencies

Ensure you have scikit-learn and other ML libraries:

```bash
queens_exam_env\Scripts\pip.exe install scikit-learn scipy
```

### Step 3: (Optional) Clean Your Data

Clean and prepare data for modeling:

```bash
python exam_analysis/run_cleaning.py
```

This creates cleaned versions in `exam_analysis/cleaned_questions.json`

### Step 4: Build Your First Model! 🎉

Run the model building script:

```bash
python models/build_first_model.py
```

This will:
1. Load questions from `exam_analysis.json`
2. Extract features (text length, word count, question type markers, etc.)
3. Build a **Question Type Classifier** (Logistic Regression)
4. Build a **Difficulty Predictor** (Random Forest)
5. Show accuracy metrics and confusion matrices

### Step 5: Review Results

The script will output:
- **Classification Accuracy**: Should be >70% for good results
- **Difficulty R² Score**: Should be >0.3 for decent prediction
- **Confusion Matrix**: Shows which types are confused
- **Feature Importance**: Shows which words/features matter most

---

## 📊 Expected Results

### If You Have 13 Exams (Current):
- ~400 questions
- **Classification Accuracy**: 60-75% (good enough to start)
- **Difficulty R²**: 0.2-0.5 (moderate prediction)

### If You Regenerate with 21 Exams:
- ~600+ questions  
- **Classification Accuracy**: 70-85% (better!)
- **Difficulty R²**: 0.4-0.6 (better prediction)

---

## 🎓 What the Model Does

### Model 1: Question Type Classification
**Predicts**: Is this an essay, multiple choice, short answer, etc.?

**Features Used**:
- Question text (TF-IDF vectors)
- Text length, word count
- Keywords ("explain", "calculate", "list")
- Multiple choice markers (a), b), c))
- Difficulty score

**Output**: Classification accuracy report showing how well it predicts question types

### Model 2: Difficulty Prediction
**Predicts**: How difficult is this question? (0-1 score)

**Features Used**:
- Question text features
- Text statistics (length, word count)
- Question type

**Output**: R² score showing prediction quality

---

## 🐛 Troubleshooting

### Problem: "Not enough questions"

**Solution**: 
- Check `exam_analysis.json` has questions
- You need at least 20 questions minimum (you have 400+, so you're fine!)

### Problem: "Accuracy < 50%"

**Possible causes**:
- Data quality issues (poor OCR, garbled text)
- Class imbalance (one type dominates)
- Need better features

**Solutions**:
- Clean data better
- Use BERT embeddings instead of TF-IDF
- Balance classes with `class_weight='balanced'` (already done)

### Problem: "Difficulty model shows low R²"

**Why**: Difficulty is hard to predict from text alone

**Solutions**:
- Use more features (course code, topic tags)
- Try different models (neural networks)
- Consider manual difficulty labeling

### Problem: Import errors (sklearn, scipy)

**Solution**:
```bash
queens_exam_env\Scripts\pip.exe install scikit-learn scipy pandas numpy
```

---

## ✅ Success Criteria

Your model is successful if:

1. **Classification Accuracy > 70%** → Good! Ready to iterate
2. **Classification Accuracy > 85%** → Excellent! Consider more complex models
3. **Difficulty R² > 0.3** → Decent prediction, can improve
4. **Difficulty R² > 0.5** → Good prediction quality

---

## 🎯 Next Steps After Building

1. **If models work well (>70% accuracy)**:
   - Try more advanced models (BERT, transformers)
   - Add more features (topics, course info)
   - Generate predictions on new questions

2. **If models struggle (<60% accuracy)**:
   - Review data quality (run data cleaning)
   - Check for class imbalance
   - Try simpler baseline models
   - Consider using pre-trained models

3. **Improve your models**:
   - Experiment with different algorithms
   - Add domain-specific features
   - Fine-tune hyperparameters
   - Use cross-validation

---

## 📝 Quick Start Command Summary

```bash
# 1. Check your data
python models/check_current_data.py

# 2. Clean data (optional but recommended)
python exam_analysis/run_cleaning.py

# 3. Build your first model!
python models/build_first_model.py
```

---

## 💡 Pro Tips

1. **Start Simple**: The script uses Logistic Regression - simple but effective
2. **Iterate Fast**: Make small changes and test quickly
3. **Use Pre-trained Models**: Consider BERT/transformers for better results
4. **Document Everything**: Keep track of what works and what doesn't
5. **Validate Properly**: The script uses train/test splits automatically

---

## 🆘 Need Help?

- **Low accuracy**: Check data quality first, then try different features
- **Import errors**: Install missing packages
- **Out of memory**: Reduce TF-IDF max_features or use smaller dataset
- **Slow training**: Normal for first run, gets faster once you optimize

**Ready? Let's build your first model!** 🚀

