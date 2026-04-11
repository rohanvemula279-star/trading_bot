# 🚀 COMPLETE HUGGING FACE DEPLOYMENT GUIDE

## Your Space URLs Will Be:
```
https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review
```

---

## STEP-BY-STEP INSTRUCTIONS

### ⚠️ BEFORE YOU START
- Have a Hugging Face account (free at https://huggingface.co)
- Have git installed on your computer
- Have your HF token ready (get it from https://huggingface.co/settings/tokens)

---

## STEP 1: Create Hugging Face Space (2 minutes)

### 1a. Go to HF Space Creator
Visit: https://huggingface.co/new-space

### 1b. Fill in the form:
```
Space name: ai-safety-review
License: MIT
Space SDK: Docker
Visibility: Public (for hackathon)
```

### 1c. Click "Create Space"
✓ Your space is now created!

---

## STEP 2: Clone Your Space (1 minute)

### 2a. Open PowerShell and run:
```powershell
cd C:\Users\rohan
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review
cd ai-safety-review
```

**Replace `YOUR_USERNAME` with your actual HF username**

Example:
```powershell
git clone https://huggingface.co/spaces/rohan/ai-safety-review
cd ai-safety-review
```

### 2b. Verify it worked:
```powershell
ls -la
# Should show: .git folder, README.md
```

---

## STEP 3: Deploy Your Project (2 minutes)

### Option A: Automatic Deployment (Recommended)

**Run this command:**
```powershell
cd C:\Users\rohan\ai-safety-review
C:\Users\rohan\HACKATHON\Deploy-to-HF.ps1 -HFUsername "YOUR_USERNAME" -SpaceName "ai-safety-review"
```

**Replace `YOUR_USERNAME` with YOUR actual username**

Example:
```powershell
C:\Users\rohan\HACKATHON\Deploy-to-HF.ps1 -HFUsername "rohan" -SpaceName "ai-safety-review"
```

This script will:
✓ Copy all your project files
✓ Verify critical files exist
✓ Clean up unnecessary files
✓ Configure git
✓ Commit changes
✓ Push to Hugging Face

**When it asks for authentication:**
- Enter your HF username (or paste the URL when asked)
- Paste your HF token as the password
- Press Enter

---

### Option B: Manual Deployment (If auto fails)

**Step 3B-1: Copy files**
```powershell
cd C:\Users\rohan\ai-safety-review

# Copy from your HACKATHON folder
Copy-Item -Path "..\HACKATHON\*" -Destination . -Recurse -Force -Exclude @(
    '.venv',
    '__pycache__',
    '*.log',
    'tmp_gradio'
)
```

**Step 3B-2: Clean up**
```powershell
# Remove unnecessary directories
Remove-Item -Path ".venv", "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue

# Remove log files
Remove-Item -Path "*.log" -Force -ErrorAction SilentlyContinue
```

**Step 3B-3: Commit to git**
```powershell
git add .
git commit -m "Deploy AI Safety Review Environment"
```

**Step 3B-4: Push to HF**
```powershell
git push
```

When prompted:
- Username: Your HF username (or press Enter if using token auth)
- Password: Paste your HF token from https://huggingface.co/settings/tokens

---

## STEP 4: Monitor the Build (5-15 minutes)

### 4a. Check Build Status
Go to: `https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review`

### 4b. Watch Build Logs
1. Click the **"Build logs"** tab
2. You should see Docker building your image
3. Look for messages like:
   ```
   Step 1/10: FROM python:3.11-slim
   Step 2/10: WORKDIR /app
   ...
   ```

### 4c. Wait for Completion
```
🟡 Building...  (takes 5-15 minutes)
    ↓
🟢 Build successful
    ↓
🟢 Space is LIVE!
```

---

## STEP 5: Verify Deployment (1 minute)

### 5a. Check if it's running
Visit: `https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review`

You should see:
- Status: 🟢 Running
- A control panel or interface
- "API" tab with endpoints

### 5b. Test the API (Optional)
Click the **"API"** tab and try making a request

---

## ✅ YOUR FINAL SPACE URL

```
https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review
```

**Use this URL for hackathon submission!**

---

## 🔧 Troubleshooting

### Problem: Git authentication failed
**Solution:**
1. Generate new token: https://huggingface.co/settings/tokens
2. Make sure it has `write` permission
3. Try again with the new token

### Problem: Build failed with "Python module not found"
**Solution:**
- Check requirements.txt is in the root
- Verify all imports use correct paths
- Run locally: `python test_environment.py`

### Problem: Docker build timeout
**Solution:**
- Your image is too large
- Or the build did complete - refresh the page
- Check Build logs tab for actual status

### Problem: Space running but shows error
**Solution:**
- Click "Settings" → "Hardware" → choose free CPU
- Restart the space
- Check logs for specific error

---

## 📋 What Gets Deployed

Your HF Space will have:
```
✓ Full AI Safety Review environment
✓ Docker containerized
✓ Runs on CPU (free) or GPU (paid)
✓ Auto-restarts on failures
✓ Public API endpoints
```

---

## 🎯 QUICK REFERENCE

| Step | Command | Time |
|------|---------|------|
| 1. Create Space | Go to https://huggingface.co/new-space | 2 min |
| 2. Clone Space | `git clone https://...` | 1 min |
| 3. Deploy Files | Run `Deploy-to-HF.ps1` | 2 min |
| 4. Monitor Build | Watch Build logs tab | 10 min |
| 5. Test | Visit your Space URL | 1 min |

**Total time: ~15 minutes**

---

## 📞 NEED HELP?

### Check HF Build Logs:
Your Space → Build logs tab → Look for errors

### Validate locally first:
```powershell
cd C:\Users\rohan\HACKATHON
python test_environment.py
```

### Manual inspection:
```powershell
# Check if files exist in your HF space directory
ls environment.py
ls models.py  
ls Dockerfile
ls requirements.txt
```

---

## YOUR NEXT STEPS

1. ✅ Create HF Space (https://huggingface.co/new-space)
2. ✅ Clone it locally
3. ✅ Run Deploy-to-HF.ps1
4. ✅ Wait for build to complete
5. ✅ Update your profile with the Space URL
6. ✅ Submit to hackathon!

**Your Space URL format:**
```
https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review
```

---

**Created:** April 11, 2026
**Status:** Ready for deployment
**Last verified:** All tests passing ✓

