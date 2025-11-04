# 🚀 Quick Start: Build Your First Model

## The Error You're Seeing

The script needs these packages installed:
- `scikit-learn` (for ML models)
- `scipy` (for scientific computing)

## Quick Fix (3 Steps)

### Step 1: Install Packages
Run this in your terminal:
```bash
queens_exam_env\Scripts\python.exe -m pip install scikit-learn scipy
```

**Note**: This takes 5-10 minutes. Let it finish!

### Step 2: Verify Installation
Run this to check:
```bash
queens_exam_env\Scripts\python.exe -c "import sklearn; import scipy; print('✅ All packages installed!')"
```

### Step 3: Run Model
```bash
python models/build_first_model.py
```

## What Will Happen

The script will:
1. ✅ Load 13 exams with ~402 questions from `exam_analysis.json`
2. ✅ Extract features (text length, word count, keywords, etc.)
3. ✅ Build a **Question Type Classifier** (predicts essay, multiple choice, etc.)
4. ✅ Build a **Difficulty Predictor** (predicts how hard a question is)
5. ✅ Show accuracy metrics and confusion matrices

## Expected Results

- **Classification Accuracy**: 60-75% (good baseline!)
- **Difficulty R²**: 0.2-0.5 (moderate prediction)

## If Installation Fails

Try these alternatives:

**Option A**: Install in PyCharm terminal
```
pip install scikit-learn scipy
```

**Option B**: Install one at a time
```
pip install scikit-learn
pip install scipy
```

**Option C**: Use conda (if you have it)
```
conda install scikit-learn scipy
```

## Troubleshooting

**"Still says module not found"**
- Make sure you're using the correct Python: `queens_exam_env\Scripts\python.exe`
- Try: `python -m pip install --upgrade pip` first
- Then: `python -m pip install scikit-learn scipy`

**"Installation is taking forever"**
- Normal! scikit-learn is large (~50MB)
- Be patient, it will finish

**"Permission denied"**
- Make sure your virtual environment is activated
- Try running as administrator

---

**Ready? Start with Step 1 above!** 🎯
