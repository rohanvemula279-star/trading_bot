# 🚀 OpenEnv Hackathon - Quick Start (TL;DR)

**Deadline:** April 8, 2026, 11:59 PM IST

## ⚡ Fast Track (5 minutes)

### 1. Run Validation First
```powershell
python validate_deployment.py
```
All checks must pass! ✅

### 2. Automated Deployment
```powershell
python deploy.py
```
Walks you through:
- ✅ Git setup
- ✅ GitHub repository
- ✅ Hugging Face deployment
- ✅ Validation check

### 3. Manual Steps (if needed)
```powershell
# Initialize Git
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo at https://github.com/new (PUBLIC)

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/your-repo.git
git push -u origin main

# Login to HuggingFace
huggingface-cli login
# Paste your token from: https://huggingface.co/settings/tokens

# Deploy to HF Spaces
openenv push --repo-id YOUR_USERNAME/my-safety-review-env
```

### 4. Submit
- Get your HF Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/my-env`
- Go to hackathon platform
- Paste the URL and submit

---

## 📋 Critical Files Checklist

| File | Status | Notes |
|------|--------|-------|
| `openenv.yaml` | ✅ | All required fields present |
| `models.py` | ✅ | SafetyAction, SafetyObservation, SafetyState |
| `graders.py` | ✅ | grade_easy_task, grade_medium_task, grade_hard_task |
| `inference.py` | ✅ | [START]/[STEP]/[END] format, < 20 min |
| `server/app.py` | ✅ | FastAPI server |
| `server/requirements.txt` | ✅ | Has openenv-core>=0.2.2 |
| `requirements.txt` | ✅ | Root dependencies |
| `Dockerfile` | ✅ | Python 3.10+, PORT 7860 |
| `README.md` | ✅ | Environment, action/observation, setup |

---

## 🆘 Troubleshooting

### `openenv push` not found
```powershell
pip install --upgrade openenv-core
```

### Docker build fails
```powershell
docker build -t test . --progress=plain
# Check Dockerfile line by line
```

### HF Space won't deploy
- Check Dockerfile is valid
- Ensure port is 7860
- Check server/requirements.txt has openenv-core
- View logs: https://huggingface.co/spaces/YOUR_USERNAME/your-space/settings

### inference.py format wrong
Must be EXACT:
```
[START] task=easy
[STEP] step=1 action=...
[END] success=true
```
NOT: `f"[START] task={task}"`

---

## 🔗 Key Links

- **Hackathon Platform:** [Link provided]
- **OpenEnv Docs:** https://github.com/meta-pytorch/OpenEnv
- **HF Spaces:** https://huggingface.co/spaces
- **Get HF Token:** https://huggingface.co/settings/tokens
- **GitHub New Repo:** https://github.com/new

---

## ✅ Final Checklist Before Submit

Run this before clicking submit:

```bash
✅ validate_deployment.py passes all checks
✅ Git repository initialized and pushed to GitHub
✅ GitHub repo is PUBLIC
✅ HF Space deployed and accessible
✅ HF Space responds to /info with HTTP 200
✅ HF Space URL is: https://huggingface.co/spaces/USERNAME/SPACE_NAME
✅ inference.py runs locally without errors
✅ inference.py output follows [START]/[STEP]/[END] format exactly
✅ All 3 tasks (easy, medium, hard) have graders
✅ README.md has all required sections
✅ Dockerfile has all required configuration
✅ No sensitive data (API keys, tokens) in code
✅ All files committed to GitHub
```

---

## 📞 If You Get Stuck

1. **Error messages:** Check DEPLOYMENT_GUIDE.md troubleshooting section
2. **Format issues:** Look at inference.py example format
3. **HF Spaces issues:** Check HF Spaces documentation
4. **OpenEnv issues:** Check OpenEnv GitHub issues
5. **Time issues:** Read the constraints - 2 vCPU, 8GB RAM, < 20 min runtime

---

**Status:** Ready to deploy! 🎉  
**Next Step:** Run `python validate_deployment.py`
