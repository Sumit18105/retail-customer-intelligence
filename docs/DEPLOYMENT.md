# Deployment Guide

```bash
git init
git add .
git commit -m "Build retail customer intelligence MVP"
git branch -M main
git remote add origin <YOUR-GITHUB-REPO-URL>
git push -u origin main
```

In Streamlit Community Cloud, select the repository and `app.py` entry point. Deploy, then test the generated URL in a clean browser. Replace the README placeholder with the actual URL. Never commit secrets.
