# 🚀 Streamlit Deployment Guide

## 💰 Cost: **FREE** (for public apps on Streamlit Cloud)

Streamlit Cloud offers **free hosting** for public apps! Perfect for sharing with friends.

---

## 🎯 Deployment Options

### Option 1: Streamlit Cloud (Recommended - FREE) ⭐

**Best for:** Sharing with friends, public access

**Cost:** FREE for public apps

**Steps:**
1. Push your code to GitHub
2. Connect to Streamlit Cloud
3. Deploy in 2 minutes

### Option 2: Self-Hosted (FREE but needs server)

**Best for:** Private apps, more control

**Cost:** FREE (if you have a server) or ~$5-10/month (VPS)

### Option 3: Other Cloud Platforms

**Best for:** Production apps with many users

**Cost:** Varies (AWS, Google Cloud, etc.)

---

## 📋 Quick Deploy: Streamlit Cloud (FREE)

### Step 1: Prepare Your Repository

Make sure you have:
- ✅ `requirements.txt` (already created)
- ✅ `web_ui/streamlit_app.py` (already created)
- ✅ Code pushed to GitHub

### Step 2: Create Streamlit Cloud Account

1. Go to: https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"

### Step 3: Deploy

1. **Connect GitHub Repository**
   - Select your repository
   - Choose branch (usually `main` or `master`)

2. **Configure App**
   - **Main file path:** `web_ui/streamlit_app.py`
   - **Python version:** 3.9 or 3.10 (auto-detected)

3. **Add Secrets (for OpenAI API key)**
   - Click "Advanced settings"
   - Add secret:
     ```
     OPENAI_API_KEY=your-actual-api-key-here
     ```
   - Or use `.streamlit/secrets.toml` format

4. **Click "Deploy"**
   - Wait 2-3 minutes
   - Your app will be live!

### Step 4: Share with Friends

Your app will be at:
```
https://your-app-name.streamlit.app
```

Share this URL with anyone! ✅

---

## 🔐 Setting Up Secrets (API Keys)

### For Streamlit Cloud:

In Streamlit Cloud dashboard:
1. Go to your app settings
2. Click "Secrets"
3. Add:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```

### For Local Development:

Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

**⚠️ Important:** Add `.streamlit/secrets.toml` to `.gitignore`!

---

## 📁 Required Files for Deployment

✅ **Already created:**
- `requirements.txt` - Python dependencies
- `web_ui/streamlit_app.py` - Main app
- `.streamlit/config.toml` - App configuration

📝 **Optional but recommended:**
- `packages.txt` - System packages (for poppler/OCR)
- `README.md` - Project documentation
- `.gitignore` - Exclude secrets

---

## 🐳 Alternative: Docker Deployment (Self-Hosted)

If you want to self-host:

### Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "web_ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Run with Docker:
```bash
docker build -t exam-generator .
docker run -p 8501:8501 exam-generator
```

---

## 🌐 Custom Domain (Optional - Costs Money)

Streamlit Cloud supports custom domains:
- **Cost:** FREE (you just need to own the domain)
- **Steps:** Add CNAME record in your domain settings

---

## 📊 Deployment Checklist

Before deploying:

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `web_ui/streamlit_app.py` works locally
- [ ] API keys stored in secrets (not in code!)
- [ ] `.gitignore` excludes secrets
- [ ] Tested locally with `streamlit run web_ui/streamlit_app.py`

---

## 🔧 Troubleshooting

### App won't deploy:
- Check `requirements.txt` syntax
- Verify main file path is correct
- Check Python version compatibility

### API keys not working:
- Verify secrets are set correctly
- Check secret name matches code (`OPENAI_API_KEY`)
- Restart app after adding secrets

### Import errors:
- Make sure all dependencies in `requirements.txt`
- Check relative imports in code
- Verify file paths are correct

### Slow loading:
- Streamlit Cloud free tier has limits
- Consider upgrading for better performance
- Or optimize your code

---

## 💡 Tips for Sharing

1. **Public Repository:** Streamlit Cloud free tier requires public GitHub repo
2. **Private Apps:** Need paid Streamlit Cloud plan OR self-host
3. **Performance:** Free tier is fine for a few users
4. **Updates:** Push to GitHub = auto-deploy (usually)

---

## 🎯 Summary

**Best Option for Sharing with Friends:**
- ✅ **Streamlit Cloud** (FREE)
- ✅ Takes 5 minutes to set up
- ✅ Auto-deploys on git push
- ✅ Share via URL
- ✅ No server maintenance needed

**Cost:** $0/month for public apps 🎉

**Ready to deploy?** Follow the "Quick Deploy" steps above!

