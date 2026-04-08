# 📋 OpenEnv Hackathon Round 1 - Submission Checklist

**Hackathon:** Meta PyTorch OpenEnv Hackathon Round 1  
**Deadline:** April 8, 2026, 11:59 PM IST  
**Problem:** AI Safety Review Environment  

---

## 🎯 Pre-Submission Validation

Run all validation before submitting:

```powershell
# 1. Run validation script
python validate_deployment.py

# 2. Test locally
python -m uvicorn server.app:app --reload --port 8000
# Visit: http://localhost:8000/docs

# 3. Test inference
python inference.py

# 4. Verify format
# Check output has [START], [STEP], [END]
```

**Result:** All checks should show ✅

---

## 📦 Code Quality Checks

- [ ] **No hardcoded API keys or tokens** in code
- [ ] **No debug logging** that would spam output
- [ ] **Proper error handling** in all functions
- [ ] **Type hints** on all functions (optional but recommended)
- [ ] **Docstrings** on complex functions
- [ ] **Requirements.txt** pinned versions (or >= constraints)
- [ ] **.gitignore** includes:
  - `__pycache__/`
  - `.env`
  - `.venv/`
  - `*.pyc`
  - `outputs/`

---

## ✅ Environment Requirements

### OpenEnv Structure
- [ ] `openenv.yaml` exists with:
  - [ ] `name`, `version`, `description`
  - [ ] `observation_space` with `type` and `module`
  - [ ] `action_space` with `type` and `module`
  - [ ] `reward_range: [0.0, 1.0]`
  - [ ] `tasks` list with easy, medium, hard
  - [ ] `graders` section with callback functions
  - [ ] All fields properly formatted

### Typed Models (`models.py`)
- [ ] `SafetyAction(Action)` dataclass
- [ ] `SafetyObservation(Observation)` dataclass
- [ ] `SafetyState(State)` dataclass
- [ ] All use `@dataclass` decorator
- [ ] All import from `openenv.core.env_server`

### Graders (`graders.py`)
- [ ] `grade_easy_task(observation, state)` function exists
- [ ] `grade_medium_task(observation, state)` function exists
- [ ] `grade_hard_task(observation, state)` function exists
- [ ] All return score in range [0.0, 1.0]
- [ ] All handle edge cases gracefully

### Server (`server/app.py`)
- [ ] FastAPI app initialized
- [ ] `/info` endpoint implemented
- [ ] `/reset` endpoint implemented
- [ ] `/step` endpoint implemented
- [ ] `/state` endpoint implemented
- [ ] Proper error handling
- [ ] CORS configured if needed

### Inference Script (`inference.py`)
- [ ] Located in **root directory** (not in server/)
- [ ] Uses `from openai import OpenAI`
- [ ] Reads environment variables:
  - [ ] `API_BASE_URL`
  - [ ] `MODEL_NAME`
  - [ ] `HF_TOKEN` or `API_KEY`
- [ ] Output format is EXACT:
  - [ ] `[START] task=<name>`
  - [ ] `[STEP] step=<n> action=<action>`
  - [ ] `[END] success=<true/false>`
- [ ] No malformed output like `[STEP step=1]`
- [ ] Script completes in < 20 minutes
- [ ] Handles API failures gracefully

### Documentation (`README.md`)
- [ ] Environment description (why it's important)
- [ ] Real-world motivation/use cases
- [ ] Action space explanation
- [ ] Observation space explanation
- [ ] State space explanation
- [ ] Task descriptions (easy, medium, hard)
- [ ] Setup instructions
- [ ] Usage example
- [ ] Grading logic explanation

### Docker (`Dockerfile`)
- [ ] Uses Python 3.10, 3.11, or 3.12 base image
- [ ] Sets `WORKDIR /app`
- [ ] Copies and installs `requirements.txt`
- [ ] Copies all source files
- [ ] Exposes port 7860
- [ ] Sets environment variables:
  - [ ] `API_BASE_URL`
  - [ ] `MODEL_NAME`
  - [ ] `HF_TOKEN`
- [ ] Has valid `CMD` or `ENTRYPOINT`
- [ ] Builds without errors: `docker build -t test .`

### Dependencies
- [ ] `requirements.txt` (root) includes:
  - [ ] `openenv-core>=0.2.2`
  - [ ] All inference dependencies (openai, etc.)
  - [ ] Pinned or constrained versions
  - [ ] No conflicting versions
- [ ] `server/requirements.txt` includes:
  - [ ] `openenv-core>=0.2.2`
  - [ ] `fastapi>=0.115.0`
  - [ ] `uvicorn>=0.24.0`
  - [ ] All server dependencies

---

## 🚀 Deployment Steps

### GitHub Setup ✅
- [ ] Repository initialized: `git init`
- [ ] Files staged and committed
- [ ] GitHub repository created (PUBLIC)
- [ ] Remote configured: `git remote add origin <url>`
- [ ] Pushed to main: `git push -u origin main`
- [ ] Repository is PUBLIC (essential for HF Spaces)
- [ ] All files visible at: https://github.com/YOUR_USERNAME/REPO_NAME

### Hugging Face Setup ✅
- [ ] Account created at https://huggingface.co
- [ ] Token generated: https://huggingface.co/settings/tokens
- [ ] CLI authenticated: `huggingface-cli login`
- [ ] OpenEnv CLI installed: `pip install openenv-core`

### Spaces Deployment ✅
- [ ] Deployed using: `openenv push --repo-id USERNAME/SPACE_NAME`
- [ ] Space is PUBLIC
- [ ] Space URL is: `https://huggingface.co/spaces/USERNAME/SPACE_NAME`
- [ ] Space responds to HTTP requests (HTTP 200)

### Verification ✅
- [ ] HF Space up and running
- [ ] `/info` endpoint responds
- [ ] `/reset` endpoint works
- [ ] `/step` endpoint works
- [ ] Space can be accessed from browser
- [ ] Dockerfile builds in HF Spaces environment
- [ ] No errors in HF Spaces logs

---

## 🎯 Task & Grading Requirements

### Easy Task
- [ ] Defined in openenv.yaml
- [ ] Difficulty: "easy"
- [ ] Max steps: specified (e.g., 50)
- [ ] Has test cases (≥ 50 recommended)
- [ ] Grader function exists: `grade_easy_task()`
- [ ] Returns score in [0.0, 1.0]
- [ ] Test cases pass locally
- [ ] Evaluation time reasonable (< 5 minutes for 50 cases)

### Medium Task
- [ ] Defined in openenv.yaml
- [ ] Difficulty: "medium"
- [ ] Max steps: specified (e.g., 100)
- [ ] Has test cases (≥ 30 recommended)
- [ ] Grader function exists: `grade_medium_task()`
- [ ] Returns score in [0.0, 1.0]
- [ ] Test cases pass locally
- [ ] Involves some complexity/edge cases

### Hard Task
- [ ] Defined in openenv.yaml
- [ ] Difficulty: "hard"
- [ ] Max steps: specified (e.g., 100)
- [ ] Has test cases (≥ 20 recommended)
- [ ] Grader function exists: `grade_hard_task()`
- [ ] Returns score in [0.0, 1.0]
- [ ] Test cases pass locally
- [ ] Requires reasoning/multi-step logic

---

## 🔒 Security & Compliance

- [ ] **No API keys in code** - use environment variables only
- [ ] **No credentials in git** - add to .gitignore
- [ ] **Environment variables in Dockerfile** - not hardcoded
- [ ] **Sensitive data logging** - disabled in production
- [ ] **.git ignored in Docker** - add to .dockerignore
- [ ] **No malicious code** - only legitimate ML/agent code

---

## 📊 Performance Requirements

| Metric | Requirement | Your Status |
|--------|-------------|-------------|
| Runtime | < 20 minutes | ✅ |
| vCPU | 2 cores | ✅ |
| Memory | 8 GB | ✅ |
| Python | 3.10+ | ✅ |
| Port | 7860 (HF Spaces) | ✅ |
| Framework | OpenEnv only | ✅ |

---

## 📝 Final Submission

### Before Clicking Submit:
```
✅ All checkboxes above completed
✅ validate_deployment.py passes all checks
✅ Local server runs: python -m uvicorn server.app:app
✅ inference.py executes without error
✅ HF Space deployed and accessible
✅ Code pushed to GitHub (PUBLIC repo)
✅ README complete with all sections
✅ No errors in HF Spaces logs
✅ Dockerfile builds successfully
```

### Submission Flow:
1. Go to hackathon platform
2. Fill in "Solution Submission" form
3. Paste your HF Spaces URL: `https://huggingface.co/spaces/USERNAME/SPACE_NAME`
4. Verify URL is public and accessible
5. Click **Submit**
6. Save confirmation email
7. You can update submission until deadline

### After Submission:
- ✅ Confirmation email received
- ✅ HF Space continues to run
- ✅ Keep GitHub repository public
- ✅ Wait for evaluation (Apr 10)
- ✅ If selected for finals: Prepare for Bangalore event (Apr 25-26)

---

## 💡 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| openenv push not found | `pip install --upgrade openenv-core` |
| HF Space won't start | Check Dockerfile, logs at HF |
| inference.py hangs | Add timeout, check API connection |
| Model returns wrong format | Review exact [START]/[STEP]/[END] format |
| Authentication failed | Generate new HF token |
| Port already in use | Change port or kill process |
| Docker build fails | Check base image, dependencies |

---

## 📚 Documentation Verification

Your README should include:
1. **Title & Description** - Clear, concise explanation
2. **Problem Statement** - Why this environment matters
3. **Real-World Applications** - Practical use cases
4. **Action Space** - What actions agent can take
5. **Observation Space** - What agent observes
6. **State Space** - Internal environment state
7. **Tasks** - Easy/Medium/Hard descriptions
8. **Grading Logic** - How scores are calculated
9. **Setup Instructions** - How to install & run
10. **Example Usage** - Code sample
11. **Installation** - Requirements, dependencies
12. **Troubleshooting** - Common issues

---

## 🎉 Ready to Submit?

Checklist complete? Then you're ready!

1. **Verify everything one more time**
2. **Run validation:** `python validate_deployment.py`
3. **Test inference:** `python inference.py`
4. **Check HF Space:** Visit your Space URL
5. **Submit to platform** with your Space URL

---

**Deadline Reminder:** April 8, 2026, 11:59 PM IST ⏰

**Good luck!** 🚀
