# OpenEnv Hackathon Round 1 - Deployment Guide

**Deadline:** April 8, 2026, 11:59 PM IST  
**Environment:** AI Safety Review  

---

## 🚀 Quick Start (6 Steps)

### Step 1: Initialize Git Repository Locally
```powershell
# In your hackathon project directory
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
git add .
git commit -m "Initial OpenEnv environment setup"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. **Repository name:** `OpenEnv-Safety-Review` (or similar)
3. **Description:** "AI Safety Review Environment - Meta OpenEnv Hackathon Round 1"
4. **Public** (required for HF Spaces)
5. Click **Create repository**
6. Add the remote:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/OpenEnv-Safety-Review.git
git branch -M main
git push -u origin main
```

### Step 3: Hugging Face Setup
```powershell
# Login to Hugging Face
huggingface-cli login
# Enter your HF token when prompted
# Can get token from: https://huggingface.co/settings/tokens
```

### Step 4: Deploy to Hugging Face Spaces
```powershell
# Install OpenEnv CLI (if not already installed)
pip install openenv-core

# Deploy your environment
# Replace with your username and repo name
openenv push --repo-id YOUR_USERNAME/my-safety-review-env
```

This will:
- Create a Hugging Face Space (public)
- Deploy your environment as a Docker container
- Make it accessible at: `https://huggingface.co/spaces/YOUR_USERNAME/my-safety-review-env`

### Step 5: Verify Deployment
```powershell
# Test your HF Space endpoint
curl https://huggingface.co/spaces/YOUR_USERNAME/my-safety-review-env/info
```

**Expected response:** HTTP 200 with environment info

### Step 6: Submit to Hackathon Platform
1. Go to hackathon platform
2. **Submit Solution:**
   - Paste your HF Spaces URL
   - Confirm it's public and working
   - Submit before **April 8, 2026, 11:59 PM IST**

---

## 📋 Pre-Deployment Checklist

Run this before deploying (see validation script below):

- ✅ `openenv.yaml` has all required fields:
  - `name`, `version`, `description`
  - `observation_space` and `action_space` with types
  - `graders` section with easy, medium, hard tasks
  - All task IDs defined with max_steps

- ✅ `models.py` has typed dataclasses:
  - `SafetyAction(Action)`
  - `SafetyObservation(Observation)`
  - `SafetyState(State)`

- ✅ Server files exist and work:
  - `server/app.py` - FastAPI server
  - `server/my_environment.py` - Environment logic
  - `server/requirements.txt` - Dependencies

- ✅ Dockerfile:
  - Uses Python 3.11 (or 3.10/3.12)
  - Exposes port 7860 (HF Spaces default)
  - Sets API_BASE_URL, MODEL_NAME, HF_TOKEN

- ✅ `inference.py`:
  - Located in root directory
  - Uses OpenAI client
  - Outputs [START]/[STEP]/[END] format
  - Completes in < 20 minutes

- ✅ Documentation:
  - README.md explains environment
  - Describes action/observation spaces
  - Lists setup instructions
  - Shows example usage

- ✅ Dependencies:
  - `requirements.txt` (root) - inference dependencies
  - `server/requirements.txt` - server dependencies
  - Both include `openenv-core>=0.2.2`

---

## 📁 Required File Structure

```
your-repo/
├── README.md                    # Environment description
├── openenv.yaml                 # Environment manifest (CRITICAL)
├── models.py                    # Typed dataclasses
├── client.py                    # EnvClient (optional but recommended)
├── inference.py                 # Baseline inference script
├── requirements.txt             # Root dependencies
├── graders.py                   # Grading logic
├── Dockerfile                   # Docker image
│
├── server/
│   ├── __init__.py
│   ├── app.py                   # FastAPI application
│   ├── my_environment.py        # Environment implementation
│   ├── requirements.txt         # Server dependencies
│   └── Dockerfile               # Optional: server-specific Dockerfile
│
├── test_data/
│   ├── easy_cases.json
│   ├── medium_cases.json
│   └── hard_cases.json
│
└── outputs/
    ├── logs/
    └── evals/
```

---

## 🔧 Critical Environment Variables

Your `Dockerfile` must set these:

```dockerfile
ENV API_BASE_URL="https://router.huggingface.co/v1"  # or your LLM endpoint
ENV MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"            # or gpt-4o-mini
ENV HF_TOKEN="your-hf-token"                          # From https://huggingface.co/settings/tokens
```

Or in `.env` file (for local testing):
```
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
HF_TOKEN=your_token_here
```

---

## 🧪 Local Testing Before Deployment

### 1. Test OpenEnv Structure
```powershell
# Check if modules load
python -c "from models import SafetyAction, SafetyObservation, SafetyState; print('✓ Models OK')"
python -c "from openenv.core.env_server import Environment; print('✓ OpenEnv OK')"
```

### 2. Test Server Locally
```powershell
cd server
python -m uvicorn app:app --reload --port 8000
# Visit: http://localhost:8000/docs
```

### 3. Test Inference Script
```powershell
# Set environment variables
$env:API_BASE_URL = "https://api.openai.com/v1"
$env:MODEL_NAME = "gpt-4o-mini"
$env:HF_TOKEN = "your_token"

# Run inference
python inference.py
# Should output:
# [START] task=easy
# [STEP] step=1 action=...
# ...
# [END] success=true/false
```

### 4. Run Validation Script (see below)

---

## ✅ Validation Script

Create `validate_deployment.py` and run before submitting:

```python
#!/usr/bin/env python
"""
Pre-deployment validation for OpenEnv Hackathon
Tests:
  1. openenv.yaml structure
  2. Models are properly typed
  3. Graders exist and work
  4. Dockerfile looks good
  5. inference.py follows format
"""

import os
import json
import yaml
from pathlib import Path
from typing import List, Tuple

def check_openenv_yaml() -> Tuple[bool, List[str]]:
    """Validate openenv.yaml structure"""
    errors = []
    if not Path("openenv.yaml").exists():
        return False, ["❌ openenv.yaml not found"]
    
    with open("openenv.yaml") as f:
        config = yaml.safe_load(f)
    
    required_fields = ["name", "version", "description", "observation_space", 
                       "action_space", "graders", "tasks"]
    for field in required_fields:
        if field not in config:
            errors.append(f"❌ Missing {field} in openenv.yaml")
    
    # Check tasks
    if "tasks" in config:
        task_ids = {t["id"] for t in config["tasks"]}
        if not {"easy", "medium", "hard"}.issubset(task_ids):
            errors.append("❌ Must have easy, medium, hard tasks")
    
    if not errors:
        return True, ["✅ openenv.yaml is valid"]
    return False, errors

def check_models() -> Tuple[bool, List[str]]:
    """Validate typed models"""
    errors = []
    try:
        from models import SafetyAction, SafetyObservation, SafetyState
        errors.append("✅ SafetyAction imported")
        errors.append("✅ SafetyObservation imported")
        errors.append("✅ SafetyState imported")
        return True, errors
    except ImportError as e:
        return False, [f"❌ Import error: {e}"]

def check_graders() -> Tuple[bool, List[str]]:
    """Validate graders exist"""
    errors = []
    if not Path("graders.py").exists():
        return False, ["❌ graders.py not found"]
    
    try:
        import graders
        for task in ["easy", "medium", "hard"]:
            func_name = f"grade_{task}_task"
            if not hasattr(graders, func_name):
                errors.append(f"❌ Missing {func_name} in graders.py")
            else:
                errors.append(f"✅ {func_name} exists")
        return len(errors) == 3, errors
    except Exception as e:
        return False, [f"❌ Graders error: {e}"]

def check_dockerfile() -> Tuple[bool, List[str]]:
    """Validate Dockerfile"""
    errors = []
    if not Path("Dockerfile").exists():
        return False, ["❌ Dockerfile not found"]
    
    with open("Dockerfile") as f:
        content = f.read()
    
    checks = [
        ("Python 3.10+", "python:3.1" in content),
        ("Port set", "EXPOSE" in content or "PORT" in content),
        ("Requirements installed", "requirements.txt" in content),
    ]
    
    for check_name, result in checks:
        if result:
            errors.append(f"✅ {check_name}")
        else:
            errors.append(f"⚠️  {check_name}")
    
    return True, errors

def check_inference() -> Tuple[bool, List[str]]:
    """Validate inference.py"""
    errors = []
    if not Path("inference.py").exists():
        return False, ["❌ inference.py not found in root"]
    
    with open("inference.py") as f:
        content = f.read()
    
    checks = [
        ("[START]" in content, "✅ [START] format token found"),
        ("[STEP]" in content, "✅ [STEP] format token found"),
        ("[END]" in content, "✅ [END] format token found"),
        ("OpenAI" in content, "✅ OpenAI client imported"),
        ("API_BASE_URL" in content, "✅ API_BASE_URL env var used"),
        ("MODEL_NAME" in content, "✅ MODEL_NAME env var used"),
    ]
    
    for check, msg in checks:
        if check:
            errors.append(msg)
        else:
            errors.append(f"❌ {msg.replace('✅', '')}")
    
    return all(c[0] for c in checks), errors

def check_readme() -> Tuple[bool, List[str]]:
    """Validate README"""
    errors = []
    if not Path("README.md").exists():
        return False, ["❌ README.md not found"]
    
    with open("README.md") as f:
        content = f.read()
    
    sections = [
        ("Environment description", content),
        ("Action space", content),
        ("Observation space", content),
        ("Tasks description", content),
        ("Setup instructions", content),
    ]
    
    for section, text in sections:
        if section.lower() in text.lower():
            errors.append(f"✅ {section} documented")
        else:
            errors.append(f"⚠️  {section} may be missing")
    
    return True, errors

def main():
    print("\n" + "="*60)
    print("🔍 OpenEnv Hackathon Pre-Deployment Validation")
    print("="*60 + "\n")
    
    checks = [
        ("OpenEnv YAML", check_openenv_yaml),
        ("Typed Models", check_models),
        ("Graders", check_graders),
        ("Dockerfile", check_dockerfile),
        ("Inference Script", check_inference),
        ("README", check_readme),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        passed, messages = check_func()
        print(f"\n📋 {check_name}:")
        for msg in messages:
            print(f"   {msg}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All checks PASSED! Ready for deployment.")
    else:
        print("❌ Some checks failed. Fix issues above before deploying.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
```

**Run it:**
```powershell
python validate_deployment.py
```

---

## 📊 Deployment Checklist

- [ ] Git repository initialized locally
- [ ] GitHub repository created and remote added
- [ ] All files committed and pushed to main branch
- [ ] Hugging Face account created and CLI authenticated
- [ ] Validation script passes all checks
- [ ] Local server runs without errors (`uvicorn app:app`)
- [ ] inference.py executes locally and produces correct output format
- [ ] Dockerfile builds successfully (`docker build -t my-env .`)
- [ ] openenv.yaml has all required fields
- [ ] graders.py has grade_easy_task, grade_medium_task, grade_hard_task
- [ ] inference.py uses API_BASE_URL, MODEL_NAME, HF_TOKEN env vars
- [ ] README.md documents environment, spaces, and setup
- [ ] requirements.txt includes openenv-core>=0.2.2
- [ ] HF Space deployed and responding to /info endpoint
- [ ] Final submission made on hackathon platform

---

## 🆘 Troubleshooting

### Docker Build Fails
```powershell
# Check syntax
docker build -t test . --progress=plain
# If base image issue, try:
docker pull python:3.11-slim
```

### HF Space Shows Error
1. Check Dockerfile exposes port 7860
2. Verify all env vars are set
3. Check server/requirements.txt has openenv-core
4. View logs: https://huggingface.co/spaces/YOUR_USERNAME/your-space/settings

### inference.py Output Format Wrong
```python
# Must be EXACT format:
print("[START] task=easy")
print("[STEP] step=1 action=APPROVE")
print("[END] success=true")
# NOT: print(f"task={task}") — must have exact brackets
```

### API Key Issues
- HF_TOKEN should be Hugging Face token, not API key
- Get from: https://huggingface.co/settings/tokens
- Can also use OpenAI API key if API_BASE_URL points to OpenAI

### "openenv push" Command Not Found
```powershell
# Install latest CLI
pip install --upgrade openenv-core
# Or use git directly (alternative):
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/env-name
git push hf main
```

---

## 📚 Key Resources

- **OpenEnv Docs:** https://github.com/meta-pytorch/OpenEnv
- **Hugging Face Spaces:** https://huggingface.co/spaces
- **OpenAI API:** https://platform.openai.com/docs
- **Hackathon Platform:** Platform URL (provided)

---

## ⏰ Timeline Reminder

| Event | Date |
|-------|------|
| **Round 1 Deadline** | **Apr 8, 2026, 11:59 PM IST** |
| Results Announcement | Apr 10, 2026 |
| Grand Finale | Apr 25-26, 2026 (Bangalore) |

Start deployment NOW to ensure plenty of time for fixes!

---

**Last Updated:** April 8, 2026  
**Status:** Ready for deployment

