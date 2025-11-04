# Quick Start: Web UI

## 🚀 Get Your UI Running in 2 Minutes

### Step 1: Install Streamlit
```bash
pip install streamlit
```

### Step 2: Set OpenAI API Key (if using question generation)
```bash
# Option 1: Environment variable
export OPENAI_API_KEY=your_key_here

# Option 2: Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Step 3: Run the UI
```bash
streamlit run web_ui/streamlit_app.py
```

### Step 4: Open Browser
The app will automatically open at: `http://localhost:8501`

---

## 🎯 What You Get

### 4 Main Pages:

1. **Generate Questions** 🤖
   - Create new questions using OpenAI
   - Select topic, difficulty, question type
   - Preview and save generated questions

2. **Question Bank** 📚
   - Browse all your existing questions
   - Filter by course, type, difficulty
   - Search questions

3. **Build Exam** 📝
   - (Coming soon) Select questions and create exams

4. **Statistics** 📊
   - View question bank stats
   - See distributions by type and course

---

## 💡 Why Streamlit?

✅ **Fast**: Get a working UI in minutes  
✅ **Easy**: No JavaScript needed  
✅ **Perfect for ML**: Built for data science/AI projects  
✅ **Iterative**: Easy to add features  

---

## 🎨 Next Steps

1. **Test it out** - Run the UI and see what works
2. **Customize** - Add features you need
3. **Upgrade later** - To FastAPI + React if needed (see `docs/UI_RECOMMENDATION.md`)

---

## 📚 Full Documentation

See `docs/UI_RECOMMENDATION.md` for:
- Detailed comparison of UI options
- When to upgrade to FastAPI + React
- Feature roadmap

---

**Ready? Run `streamlit run web_ui/streamlit_app.py` and start generating!** 🎉

