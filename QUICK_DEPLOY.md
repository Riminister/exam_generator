# 🚀 Quick Deploy to Streamlit Cloud (FREE)

## Step-by-Step Guide (5 minutes)

### ✅ Prerequisites
- GitHub account (free)
- Code pushed to GitHub
- OpenAI API key (if using question generation)

---

## 📝 Step 1: Push Code to GitHub

If you haven't already:

```bash
git init
git add .
git commit -m "Initial commit with Streamlit app"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click "Sign in" (use GitHub)

2. **Create New App**
   - Click "New app"
   - Select your repository
   - Select branch (`main` or `master`)

3. **Configure App**
   - **Main file path:** Use the direct GitHub URL to the file:
     ```
     https://github.com/Riminister/exam_generator/blob/master/web_ui/streamlit_app.py
     ```
     OR just the relative path: `web_ui/streamlit_app.py`
   - Python version: Auto-detected (3.9 or 3.10)

4. **Add Secrets (for OpenAI)**
   - Click "Advanced settings"
   - Click "Secrets"
   - Add:
     ```
     OPENAI_API_KEY = "sk-your-actual-key-here"
     ```
   - Save

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - ✅ Done!

---

## 🔗 Step 3: Share Your App

Your app URL will be:
```
https://your-app-name.streamlit.app
```

Share this with your friends! 🎉

---

## 💰 Cost: **FREE**

- ✅ Unlimited apps
- ✅ Public apps are free
- ✅ Auto-deploys on git push
- ✅ No credit card needed

**Note:** Private apps require paid plan, but public apps are free!

---

## 🔄 Updates

Every time you push to GitHub:
1. Streamlit Cloud auto-detects changes
2. Auto-redeploys your app
3. Friends see updates immediately

---

## 🐛 Troubleshooting

**"App won't deploy"**
- Check main file path is correct
- Verify `requirements.txt` exists
- Check for syntax errors

**"API key not working"**
- Verify secret name: `OPENAI_API_KEY`
- Check secret is saved correctly
- Restart app after adding secrets

**"Import errors"**
- Make sure all dependencies in `requirements.txt`
- Check file paths are correct

---

## 📚 Full Guide

See `DEPLOYMENT_GUIDE.md` for:
- Self-hosting options
- Docker deployment
- Custom domains
- Advanced configuration

---

**That's it! Your app is live and free!** 🎉

