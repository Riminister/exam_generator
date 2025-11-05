# Streamlit Cloud Deployment - Correct URL Format

## ✅ Correct URL for Streamlit Cloud

When Streamlit Cloud asks for the **main file path**, use one of these:

### Option 1: Direct GitHub URL (Recommended)
```
https://github.com/Riminister/exam_generator/blob/master/web_ui/streamlit_app.py
```

### Option 2: Relative Path (Alternative)
```
web_ui/streamlit_app.py
```

## 📋 Complete Deployment Steps

1. **Go to Streamlit Cloud**: https://share.streamlit.io/
2. **Sign in** with GitHub
3. **Click "New app"**
4. **Repository**: `https://github.com/Riminister/exam_generator`
5. **Main file path**: 
   ```
   https://github.com/Riminister/exam_generator/blob/master/web_ui/streamlit_app.py
   ```
   OR
   ```
   web_ui/streamlit_app.py
   ```
6. **Branch**: `master`
7. **Add Secret** (for OpenAI):
   - Click "Advanced settings" → "Secrets"
   - Add:
     ```
     OPENAI_API_KEY = "sk-your-actual-key-here"
     ```
8. **Click "Deploy"**

## ✅ Your App Will Be Live At:
```
https://exam-generator.streamlit.app
```
(or similar URL based on your app name)

---

**Note:** Streamlit Cloud accepts both formats:
- Full GitHub URL to the file
- Relative path from repository root

Both work! Use whichever Streamlit Cloud prefers.

