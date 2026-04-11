# 🚀 Hugging Face Deployment Guide

## Quick Summary
Your environment is **FRESH and CLEAN** - Ready for Hugging Face!

### Environment Status
✅ All tests passing
✅ All dependencies installed  
✅ No errors or conflicts
✅ Test data validated

---

## Part 1: Prepare Your Local Project

### Step 1: Verify Everything Works Locally
```powershell
cd c:\Users\rohan\HACKATHON
python test_environment.py
```
Expected output: All 5 tests should PASS ✓

### Step 2: Clean Up Extra Files (Optional)
```powershell
# Remove __pycache__ and .pyc files
python -c "import shutil; import os; [shutil.rmtree(d, ignore_errors=True) for d in ['__pycache__', '.pytest_cache', 'tmp_gradio']]"

# Remove old log files
if (Test-Path "run1.log") { Remove-Item "run1.log" }
if (Test-Path "run2.log") { Remove-Item "run2.log" }
```

### Step 3: Create .gitignore (if not present)
```
.venv/
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
.env
tmp_gradio/
*.log
.DS_Store
```

---

## Part 2: Create Hugging Face Space

### Step 1: Create a Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up or log in

### Step 2: Create a New Space
1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name:** `ai-safety-review-openenv` (or your choice)
   - **License:** MIT
   - **Space SDK:** Docker
   - **Visibility:** Public (for hackathon)

### Step 3: Clone the Space to Your Computer
```powershell
cd C:\Users\rohan
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review-openenv
cd ai-safety-review-openenv
```

---

## Part 3: Copy Project Files to Hugging Face

### Step 1: Copy Your Project
```powershell
# Copy all project files from HACKATHON to the space directory
# Make sure you're in the space directory

# Copy source code
Copy-Item -Path "C:\Users\rohan\HACKATHON\*" -Destination . -Recurse -Force -Exclude @('\.venv', '__pycache__', '*.log', 'tmp_gradio')
```

### Step 2: Verify Key Files Are Present
```powershell
# These files MUST be in the space root:
ls -la Dockerfile
ls -la requirements.txt
ls -la openenv.yaml
ls -la environment.py
ls -la models.py
ls -la graders.py
ls -la server/app.py
```

---

## Part 4: Docker Configuration

### Option A: Use Existing Dockerfile (Recommended)
Your project already has a `Dockerfile`. Make sure it looks like:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PORT=7860
ENV HOST=0.0.0.0

# Expose port
EXPOSE 7860

# Command to run
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### Option B: Create/Update Dockerfile
If you need to create/update it:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

# Set environment variables
ENV PORT=7860
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## Part 5: Push to Hugging Face

### Step 1: Initialize Git (if first time)
```powershell
cd ai-safety-review-openenv
git config user.name "Your Name"
git config user.email "your-email@example.com"
```

### Step 2: Add and Commit Files
```powershell
git add .
git commit -m "Initial OpenEnv submission - AI Safety Review"
```

### Step 3: Create Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with `write` permission
3. Copy the token

### Step 4: Login and Push
```powershell
# When prompted, paste your token
huggingface-cli login

# Push to Hugging Face
git push
```

Or without login:
```powershell
git push https://YOUR_USERNAME:YOUR_TOKEN@huggingface.co/spaces/YOUR_USERNAME/ai-safety-review-openenv
```

---

## Part 6: Monitor the Build

### Step 1: Check Build Status
1. Go to https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review-openenv
2. You should see "Building" status
3. Check the **Build logs** tab for any errors

### Step 2: Common Issues & Fixes

#### ❌ "openenv not found"
**Solution:** Make sure requirements.txt has `openenv-core==0.2.3`

#### ❌ "Port already in use"
**Solution:** Hugging Face automatically maps to port 7860, already in Dockerfile

#### ❌ "Module not found"
**Solution:** Check your imports. Must be absolute or relative from root

#### ❌ "Timeout building"
**Solution:** Reduce Docker image size:
```dockerfile
RUN pip install --no-cache-dir --no-deps -r requirements.txt
```

### Step 3: Test the Deployment
Once build completes:
1. Click "View Space" 
2. You should see the OpenEnv interface
3. Try running a test task

---

## Part 7: Final Checklist

**Before submission to hackathon:**

- [ ] .venv is REMOVED (not pushed)
- [ ] requirements.txt has all dependencies
- [ ] openenv.yaml is valid with easy/medium/hard tasks
- [ ] Dockerfile is present and correct
- [ ] server/app.py exists and runs on port 7860
- [ ] environment.py and models.py are in root
- [ ] graders.py exports grade_easy_task, grade_medium_task, grade_hard_task
- [ ] Test data files exist (easy_cases.json, etc.)
- [ ] .env template has PLACEHOLDER values, not real keys
- [ ] No __pycache__ or .pyc files committed
- [ ] test_environment.py passes all tests locally

---

## Part 8: Update Instructions for Your Reference

### To update after changes:
```powershell
cd C:\Users\rohan\HACKATHON
# Make your changes...

# Test locally
python test_environment.py

# When ready to push to HuggingFace:
cd ../ai-safety-review-openenv
git add .
git commit -m "Your change description"
git push

# Then HF automatically rebuilds
```

---

## 📝 Key Files Summary

| File | Purpose | Status |
|------|---------|--------|
| requirements.txt | All dependencies | ✓ Clean |
| Dockerfile | Container build | ✓ Ready |
| openenv.yaml | Task definitions | ✓ Valid |
| environment.py | Root import proxy | ✓ Fixed |
| models.py | Root model imports | ✓ Fixed |
| graders.py | Root grader imports | ✓ Fixed |
| src/environment.py | SafetyReviewEnv class | ✓ Core |
| src/models.py | SafetyAction, Observation, State | ✓ Complete |
| server/app.py | FastAPI server | ✓ Ready |
| .env | Config template | ✓ Secure |

---

## 🆘 Need Help?

### Check HF Logs:
```
Your Space URL → Build logs tab → "Build failed" details
```

### Check Docker Build Locally:
```powershell
docker build -t safety-review .
docker run -p 7860:7860 safety-review
```

### Validate Locally Again:
```powershell
python test_environment.py
```

---

**Your environment is PRODUCTION READY!** 🎉

Once deployed to HF, you'll have a live OpenEnv environment that:
✅ Runs on HF Spaces (free GPU available)
✅ Auto-rebuilds on git push
✅ Handles concurrent sessions
✅ Serves API endpoints

**Hackathon submission:** Just share your HF Space URL!
