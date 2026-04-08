# 🔧 OpenEnv Hackathon - Troubleshooting Guide

**Common deployment problems and solutions**

---

## 🔴 Critical Issues (Fix Immediately)

### ❌ "openenv not found" / "openenv_core import failed"

**Problem:** Can't import openenv or openenv CLI not available

**Solution:**
```powershell
# Reinstall
pip uninstall openenv-core -y
pip install openenv-core --upgrade

# Verify
python -c "from openenv.core.env_server import Environment; print('OK')"
openenv --version
```

**If still fails:**
```powershell
# Show active Python
python --version
python -c "import sys; print(sys.executable)"

# Create fresh venv
python -m venv venv_new
./venv_new/Scripts/Activate.ps1
pip install openenv-core
```

---

### ❌ "Dockerfile not found" or "Docker build fails"

**Problem:** Docker can't find or build Dockerfile

**Solution:**
```powershell
# Verify Dockerfile exists
Test-Path Dockerfile

# Check Dockerfile syntax
docker build -t test . --progress=plain

# If base image missing
docker pull python:3.11-slim

# Build again
docker build -t test .
```

**Dockerfile common issues:**
```dockerfile
# ❌ WRONG - typo in path
COPY requirements txt .

# ✅ CORRECT
COPY requirements.txt .

# ❌ WRONG - missing EXPOSE
CMD ["python", "server.py"]

# ✅ CORRECT  
EXPOSE 7860
CMD ["python", "server.py"]

# ❌ WRONG - old Python
FROM python:2.7

# ✅ CORRECT
FROM python:3.11-slim
```

---

### ❌ "inference.py format wrong" / "Evaluation failed"

**Problem:** Output format doesn't match expected format

**Solution:**
Your output MUST be exactly:
```
[START] task=easy
[STEP] step=1 action=APPROVE
[STEP] step=2 action=FLAG
[END] success=true
```

**Common format mistakes:**
```python
# ❌ WRONG - Extra brackets
print("[STEP step=1 action=APPROVE]")

# ❌ WRONG - Missing brackets
print("STEP step=1 action=APPROVE")

# ❌ WRONG - Different field names
print("[STEP] step=1 action=APPROVE reasoning=...")

# ❌ WRONG - f-string interpolation shows wrong brackets
action_str = "[STEP] step=1 action=APPROVE"
print(f"[STEP] step=1 action={actual_action}")  # If actual_action is "APPROVE", this is OK

# ✅ CORRECT - Exact format
print("[START] task=easy")  # NO newlines, NO extra spaces
for step in range(1, 4):
    print(f"[STEP] step={step} action=APPROVE")
print("[END] success=true")
```

**Test locally:**
```powershell
python inference.py > output.txt
# Check output.txt for exact format
cat output.txt
```

---

### ❌ HF Space won't start / "Build failed"

**Problem:** HF Space shows error or doesn't respond

**Solutions:**

1. **Check Dockerfile**
   ```dockerfile
   # Must have port 7860
   EXPOSE 7860
   
   # Or set environment variable
   ENV PORT=7860
   
   # Start command must be correct
   CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

2. **Check server/requirements.txt**
   ```
   openenv-core>=0.2.2
   fastapi>=0.115.0
   uvicorn>=0.24.0
   ```

3. **Check server/app.py exists**
   ```powershell
   Test-Path server/app.py
   ```

4. **View HF Spaces logs**
   - Go to: https://huggingface.co/spaces/YOUR_USERNAME/your-space
   - Click "Settings" → "Logs"
   - Look for error messages

5. **Test locally first**
   ```powershell
   cd server
   python -m uvicorn app:app --host 0.0.0.0 --port 7860
   # Should show: "Application startup complete"
   ```

---

## ⚠️ Warning Issues (May cause failures)

### ⚠️ "API key authentication failed"

**Problem:** Can't connect to LLM API

**Solution:**
```powershell
# Check env var is set
$env:HF_TOKEN
$env:API_BASE_URL
$env:MODEL_NAME

# Or in .env file
cat .env

# Test OpenAI client
python -c "from openai import OpenAI; c = OpenAI(api_key='test'); print('OK')"
```

**Common issues:**
- Token is expired - get new token
- Token has wrong permissions - needs 'write' access
- API_BASE_URL is wrong format
- MODEL_NAME doesn't exist

---

### ⚠️ "Python version mismatch"

**Problem:** Code works locally but fails on HF Space

**Causes:** Python 2 vs 3, version differences

**Solution:**
```powershell
# Check your Python
python --version
# Should be 3.10, 3.11, or 3.12

# Update Dockerfile base image
FROM python:3.11-slim  # ✅ Good
FROM python:3.10-slim  # ✅ Good
FROM python:2.7        # ❌ Bad - too old
```

**In requirements.txt, specify:**
```
# ❌ WRONG - vague
numpy
fastapi

# ✅ CORRECT - specific versions
numpy>=1.21.0
fastapi>=0.115.0
```

---

### ⚠️ "Models can't be imported" / "Import errors"

**Problem:** `from models import SafetyAction` fails

**Solutions:**

1. **Check file exists**
   ```powershell
   Test-Path models.py
   ```

2. **Check imports are correct**
   ```python
   # ❌ WRONG
   from openenv import Action
   
   # ✅ CORRECT
   from openenv.core.env_server import Action, Observation, State
   ```

3. **Check models file for syntax errors**
   ```python
   # ❌ WRONG - missing @dataclass
   class SafetyAction:
       command: str
   
   # ✅ CORRECT
   from dataclasses import dataclass
   from openenv.core.env_server import Action
   
   @dataclass
   class SafetyAction(Action):
       command: str
   ```

4. **Check __init__.py**
   ```python
   # In my_trading_env/__init__.py
   from .models import SafetyAction, SafetyObservation, SafetyState
   from .client import EnvClient
   from .server.my_environment import SafetyReviewEnv
   ```

---

### ⚠️ "Timeout / Script takes too long"

**Problem:** inference.py runs > 20 minutes

**Solutions:**

1. **Add timeout handling**
   ```python
   import signal
   
   def timeout_handler(signum, frame):
       raise TimeoutError("Execution timeout")
   
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(900)  # 15 minutes
   
   try:
       # Your code
       pass
   except TimeoutError:
       print("[END] success=false")
   finally:
       signal.alarm(0)  # Cancel alarm
   ```

2. **Reduce test cases**
   - Don't test all 50+ cases
   - Sample representative cases

3. **Cache API responses**
   ```python
   import json
   from pathlib import Path
   
   cache_file = Path(".api_cache.json")
   cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
   
   # Use cache before API call
   key = f"{task}_{input_data}"
   if key in cache:
       response = cache[key]
   else:
       response = api.call(...)
       cache[key] = response
   
   # Save for next run
   cache_file.write_text(json.dumps(cache))
   ```

---

## 🔵 Minor Issues (Warnings but may not fail)

### ⚠️ "Git push fails" / "Authentication"

**Problem:** GitHub authentication fails

**Solutions:**

1. **Use HTTPS with token**
   ```powershell
   git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
   git push origin main
   ```

2. **Use SSH (better)**
   ```powershell
   # Generate SSH key
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   # Add to GitHub: https://github.com/settings/keys
   cat ~/.ssh/id_ed25519.pub  # Copy this
   
   # Use SSH URL
   git remote set-url origin git@github.com:USERNAME/REPO.git
   git push origin main
   ```

3. **Clear credential cache**
   ```powershell
   git credential-manager-core erase <url>
   ```

---

### ⚠️ "openenv push not recognized"

**Problem:** Command `openenv push` doesn't work

**Solutions:**

1. **Install/upgrade**
   ```powershell
   pip install --upgrade openenv-core
   ```

2. **Verify installation**
   ```powershell
   pip show openenv-core
   which openenv  # or: cmd /c where openenv
   ```

3. **Use alternative deployment**
   ```powershell
   # Direct GitHub to HF Spaces link
   # (Contact HF support for manual setup)
   ```

---

### ⚠️ "README sections missing"

**Problem:** README incomplete

**Solutions:**

Add these sections to README.md:
```markdown
# Environment Name

## Description
[What is this environment? Why is it important?]

## Real-World Applications
- Use case 1
- Use case 2

## Action Space
[Describe what actions agent can take]

## Observation Space
[Describe what agent observes]

## State Space
[Describe internal state]

## Tasks

### Easy Task
[Description, difficulty level, max steps]

### Medium Task
[Description, difficulty level, max steps]

### Hard Task
[Description, difficulty level, max steps]

## Grading Logic
[Explain how scores are calculated]

## Setup

### Prerequisites
- Python 3.10+
- [Other requirements]

### Installation
```bash
pip install -r requirements.txt
```

### Running Locally
```bash
cd server
python -m uvicorn app:app
```

## Example Usage
```python
[Code example]
```

## Troubleshooting
[Common issues]
```

---

## 🆘 Still Stuck?

### Check these in order:

1. **Validation script**
   ```powershell
   python validate_deployment.py
   # Read error messages carefully
   ```

2. **Local tests**
   ```powershell
   # Test models
   python -c "from models import *; print('OK')"
   
   # Test server
   cd server
   python -m uvicorn app:app --log-level debug
   
   # Test graders
   python -c "from graders import *; print('OK')"
   ```

3. **Docker test**
   ```powershell
   docker build -t test . --progress=plain
   docker run -p 8000:7860 test
   ```

4. **HF Spaces logs**
   - Go to your Space settings
   - Check "Logs" for errors

5. **Hackathon forum/support**
   - Check if others had same issue
   - Post question with error message

---

## 📞 Getting Help

**Include when asking for help:**
1. Full error message (not truncated)
2. What you've tried so far
3. Your OS (Windows/Mac/Linux)
4. Python version
5. Which file is problematic

**Example:**
```
"Getting error when running `python validate_deployment.py`:
  Error: ModuleNotFoundError: No module named 'openenv'
  
What I tried:
  - pip install openenv-core
  - pip uninstall openenv-core && pip install openenv-core
  
Python: 3.11.2
OS: Windows 11
"
```

---

**Status:** Created Apr 8, 2026  
**Last Updated:** Apr 8, 2026
