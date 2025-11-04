# Notebooks Directory

This directory contains Jupyter notebooks for exploratory data analysis and model development.

## 📓 Available Notebooks

### `exploratory_analysis.ipynb`
Comprehensive exploratory data analysis of your exam dataset. This notebook:

- **Loads and examines** your exam data
- **Visualizes** question distributions, types, and patterns
- **Analyzes** difficulty scores and question lengths
- **Identifies** data quality issues
- **Provides** recommendations for model building

**Usage:**
```bash
# Make sure you're in the project root
jupyter notebook notebooks/exploratory_analysis.ipynb
```

Or if using VS Code or PyCharm, just open the `.ipynb` file directly.

## 🚀 Quick Start

1. **Install Jupyter** (if not already installed):
   ```bash
   pip install jupyter notebook
   ```

2. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```
   This will open in your browser.

3. **Navigate** to the `notebooks/` folder and open `exploratory_analysis.ipynb`

4. **Run all cells** to see the complete analysis, or run cells one by one to explore step-by-step.

## 📊 What You'll Learn

After running the exploratory analysis notebook, you'll understand:

- ✅ Dataset size and composition
- ✅ Question type distribution (essay, multiple choice, etc.)
- ✅ Difficulty patterns across courses
- ✅ Topic coverage
- ✅ Data quality issues to address
- ✅ Relationships between features
- ✅ Recommendations for model building

## 💡 Tips

- **Run cells sequentially** - Each cell builds on previous ones
- **Modify parameters** - Adjust thresholds, colors, or plot types
- **Export results** - Use the final cell to save summary statistics
- **Iterate** - Come back to this notebook as your data changes

## 🎯 Next Steps

After exploring your data:

1. **Clean the data**: `python exam_analysis/run_cleaning.py`
2. **Build models**: `python models/build_first_model.py`
3. **Iterate** based on what you learned from the analysis

Happy exploring! 🚀

