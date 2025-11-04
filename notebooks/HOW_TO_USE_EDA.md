# How to Use Exploratory Data Analysis - Step-by-Step Guide

## 🎯 Purpose of Exploratory Data Analysis (EDA)

**Before building ML models**, you need to:
1. **Understand your data** - What do you have? Is it clean?
2. **Identify patterns** - Are there relationships between features?
3. **Find issues** - Missing data, outliers, class imbalance?
4. **Make informed decisions** - What models make sense? What features to use?

This notebook helps you do all of that!

---

## 📋 Step-by-Step Process

### **Step 1: Run the Notebook**

#### Option A: Using Jupyter Notebook
```bash
# In your terminal (from project root)
jupyter notebook notebooks/exploratory_analysis.ipynb
```

#### Option B: Using VS Code or PyCharm
- Just open `notebooks/exploratory_analysis.ipynb` in your IDE
- Click "Run All" or run cells one by one (Shift+Enter)

#### Option C: Using JupyterLab
```bash
jupyter lab notebooks/exploratory_analysis.ipynb
```

---

### **Step 2: Understand Each Section**

#### **Section 1: Setup and Imports** ✅
- **What it does**: Loads libraries (pandas, matplotlib, etc.)
- **What to check**: Make sure all imports succeed (no errors)
- **Action**: If errors occur, install missing packages: `pip install pandas matplotlib seaborn numpy`

#### **Section 2: Load Data** 📊
- **What it does**: Loads your `data/exam_analysis.json` file
- **What to look for**: 
  - ✅ Should show number of exams loaded
  - ✅ Should show total questions
- **If it fails**: Check that `data/exam_analysis.json` exists

#### **Section 3: Convert to DataFrame** 🔄
- **What it does**: Converts JSON to a pandas DataFrame (table)
- **What to look for**: 
  - DataFrame shape (rows × columns)
  - List of columns available
  - Preview of first few rows
- **Action**: Review the columns - these are your **features** for ML models!

#### **Section 4: Basic Statistics** 📈
- **What it shows**:
  - Total questions, exams, courses
  - Question type distribution
  - Course distribution
- **What to look for**:
  - ✅ Are there enough questions? (You have 201 - good for starting!)
  - ✅ Are question types balanced? (If one type has 90%, that's imbalanced)
  - ✅ How many courses? (13 courses - good diversity)
- **Action**: Note any class imbalance - you'll need to handle this in models

**Example Interpretation**:
```
Total Questions: 201
Question Types:
  essay: 51 (25%)     ← Good balance
  other: 83 (41%)     ← Largest category
  short_answer: 38 (19%)
```

#### **Section 5: Question Type Visualization** 📊
- **What it shows**: Bar charts and pie charts of question types
- **What to look for**:
  - **Class imbalance**: If one type dominates (>60%), use class weights in models
  - **Missing types**: Are expected types missing?
- **Action**: 
  - If imbalanced: Plan to use `class_weight='balanced'` in sklearn models
  - Note which types you want to predict

#### **Section 6: Question Length Analysis** 📏
- **What it shows**: 
  - Distribution of question lengths
  - Length by question type
  - Violin plots showing spread
- **What to look for**:
  - **Outliers**: Very long questions (>5000 chars) might be errors
  - **Patterns**: Do essay questions tend to be longer? (Probably yes!)
  - **Normal distribution?**: If skewed, use log transform
- **Action**:
  - Very short questions (<20 chars): Review for data quality issues
  - Very long questions: Might need special handling
  - **Feature idea**: Question length is a good feature for classification!

#### **Section 7: Difficulty Score Analysis** 🎯
- **What it shows**:
  - Distribution of difficulty scores
  - Difficulty by question type
  - Relationship between length and difficulty
- **What to look for**:
  - **Coverage**: How many questions have difficulty > 0? 
    - If <50%, difficulty prediction might be hard
  - **Correlation**: Does longer = more difficult?
    - If correlation > 0.3, length is a useful feature
  - **Patterns**: Do certain question types have higher difficulty?
- **Action**:
  - If many zeros: Difficulty prediction might need more data or better features
  - If good coverage: You can build a difficulty prediction model
  - Use difficulty as a feature for other models

#### **Section 8: Data Quality Checks & Summary** 🔍
- **What it shows**:
  - Missing values
  - Short questions (potential errors)
  - Zero difficulty scores
  - Topic coverage
  - Summary recommendations
- **What to look for**:
  - ❌ **Missing values**: Need to handle (drop or impute)
  - ⚠️ **Short questions**: Might be noise or incomplete
  - ⚠️ **Zero difficulty**: Need assessment or remove from difficulty model
  - ⚠️ **Low topic coverage**: Consider running topic extraction
- **Action**: Based on findings, decide:
  - Run data cleaning? (YES - recommended!)
  - Build models now? (YES if data looks good)
  - Need more data? (Depends on quality)

---

## 🎯 What to Do Based on Findings

### **Scenario 1: Data Looks Good** ✅
If you see:
- ✅ No missing values
- ✅ Balanced question types
- ✅ Good difficulty coverage (>50%)
- ✅ Reasonable length distribution

**Next Steps**:
1. ✅ Run data cleaning: `python exam_analysis/run_cleaning.py`
2. ✅ Build first model: `python models/build_first_model.py`
3. ✅ Evaluate results
4. ✅ Iterate and improve

### **Scenario 2: Class Imbalance** ⚠️
If one question type dominates (>60%):

**Actions**:
- Use `class_weight='balanced'` in sklearn models
- Use stratified train/test split
- Consider SMOTE for oversampling (if needed)
- Focus on most common types first

### **Scenario 3: Poor Data Quality** ❌
If you find:
- Many missing values
- Many very short/long questions
- Low difficulty coverage

**Actions**:
1. **Run data cleaning FIRST**: `python exam_analysis/run_cleaning.py`
2. Review cleaned data
3. Decide if you need more data
4. Then build models

### **Scenario 4: Small Dataset** 📉
If you have <100 questions:

**Actions**:
- Start with simple models (logistic regression)
- Use cross-validation (not just train/test split)
- Consider transfer learning (pre-trained models)
- Plan to download more exams later

---

## 📊 Key Metrics to Watch

### **For Classification Models**:
1. **Class balance**: Is one type >60%? → Use class weights
2. **Feature availability**: Do you have text + metadata? → Good for models
3. **Sample size**: <50 per class? → Use simple models first

### **For Regression Models** (Difficulty):
1. **Coverage**: >50% have difficulty scores? → Can build model
2. **Distribution**: Normal or skewed? → Use appropriate metrics
3. **Correlations**: Length correlates with difficulty? → Use as feature

---

## 🔄 Iterative Process

EDA is not one-time! Do it:
1. **Before cleaning** - Understand raw data
2. **After cleaning** - Verify improvements
3. **After model training** - Understand errors
4. **When adding new data** - Check changes

---

## 💡 Pro Tips

1. **Save outputs**: The notebook can save summary CSVs - use them!
2. **Modify parameters**: Change thresholds, colors, bins to explore
3. **Ask questions**: Why is X correlated with Y? What does this mean?
4. **Document findings**: Take notes on what you discover
5. **Compare before/after**: Run EDA before and after cleaning

---

## 🎯 Quick Decision Tree

```
Run EDA Notebook
│
├─ Data looks clean? 
│  ├─ YES → Run cleaning → Build models
│  └─ NO → Run cleaning → Re-run EDA → Build models
│
├─ Enough data?
│  ├─ YES (>100 questions) → Build models
│  └─ NO (<100 questions) → Use simple models or get more data
│
├─ Class imbalance?
│  ├─ YES → Use class weights, stratified splits
│  └─ NO → Standard train/test split is fine
│
└─ Difficulty coverage good?
   ├─ YES (>50%) → Build difficulty model
   └─ NO (<50%) → Skip difficulty model, focus on classification
```

---

## 📝 Checklist After Running EDA

- [ ] Reviewed all visualizations
- [ ] Noted any data quality issues
- [ ] Identified class imbalances
- [ ] Checked feature distributions
- [ ] Reviewed summary recommendations
- [ ] Decided on next steps (clean? model? get more data?)
- [ ] Documented key findings

---

## 🚀 Next Steps After EDA

1. **Clean the data**: `python exam_analysis/run_cleaning.py`
2. **Review cleaned data**: Run EDA again on cleaned data
3. **Build first model**: `python models/build_first_model.py`
4. **Evaluate results**: Did model performance match EDA insights?
5. **Iterate**: Improve models based on findings

---

## ❓ Common Questions

**Q: Do I need to understand every chart?**
A: No! Focus on the summary and recommendations. Charts are visual aids.

**Q: What if I find errors?**
A: That's great! EDA found issues before they hurt your models. Fix them first.

**Q: How long should EDA take?**
A: First time: 30-60 min. Subsequent runs: 10-15 min.

**Q: Should I run EDA after every change?**
A: Yes, especially after cleaning or adding new data.

---

## 🎓 Learning Resources

- **Pandas**: https://pandas.pydata.org/docs/
- **Matplotlib**: https://matplotlib.org/stable/tutorials/
- **Seaborn**: https://seaborn.pydata.org/tutorial.html

---

**Remember**: EDA is exploration - there are no wrong answers, only discoveries! 🔍✨

