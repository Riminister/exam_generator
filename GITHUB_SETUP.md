# 🚀 GitHub Setup for Streamlit Deployment

## Step 1: Create GitHub Repository

1. **Go to GitHub**: https://github.com/new
2. **Create new repository**:
   - Repository name: `exam-generator` (or your preferred name)
   - Description: "AI-powered exam question generator"
   - Visibility: **Public** (required for free Streamlit Cloud)
   - **Don't** initialize with README (you already have code)
3. **Click "Create repository"**

## Step 2: Get Your Repository URL

After creating, GitHub will show you the URL. It will look like:
```
https://github.com/YOUR_USERNAME/exam-generator.git
```

**Or if using SSH:**
```
git@github.com:YOUR_USERNAME/exam-generator.git
```

## Step 3: Connect Your Local Code to GitHub

Run these commands in your project directory:

```bash
# Add all files
git add .

# Commit
git commit -m "Add Streamlit app and deployment files"

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git push -u origin master
```

## Step 4: Use in Streamlit Cloud

When deploying in Streamlit Cloud, use:

**Option 1: HTTPS (Easiest)**
```
https://github.com/YOUR_USERNAME/REPO_NAME
```

**Option 2: SSH**
```
git@github.com:YOUR_USERNAME/REPO_NAME.git
```

**Note:** Just paste the URL without `.git` at the end if using HTTPS.

---

## Quick Commands

After creating your GitHub repo, run:

```bash
# Replace with your actual GitHub username and repo name
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main  # Optional: rename branch to main
git push -u origin main  # or master if that's your branch
```

---

## Example

If your GitHub username is `danie123` and repo is `exam-generator`:

**GitHub URL:**
```
https://github.com/danie123/exam-generator
```

**Streamlit Cloud:**
- Paste: `https://github.com/danie123/exam-generator`
- Branch: `main` or `master`
- Main file: `web_ui/streamlit_app.py`

---

## Need Help?

If you haven't created the GitHub repo yet:
1. Go to https://github.com/new
2. Create repository
3. Copy the URL it shows you
4. Use that URL in the commands above

