@echo off
REM ============================================================================
REM HUGGING FACE DEPLOYMENT AUTOMATION SCRIPT
REM ============================================================================
REM This script prepares your project for Hugging Face deployment
REM
REM BEFORE RUNNING:
REM 1. Create HF Space: https://huggingface.co/new-space
REM    - Space name: ai-safety-review
REM    - SDK: Docker
REM    - Visibility: Public
REM 2. Clone: git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-safety-review
REM 3. Open that folder in PowerShell
REM 4. Run this script
REM ============================================================================

@echo.
@echo ============================================================================
@echo HUGGING FACE SPACE DEPLOYMENT ASSISTANT
@echo ============================================================================
@echo.

REM Get user info
set /p HF_USERNAME=Enter your Hugging Face username: 
set /p SPACE_NAME=Enter your Space name (e.g., ai-safety-review): 

@echo.
@echo ============================================================================
@echo STEP 1: COPY PROJECT FILES
@echo ============================================================================
@echo Copying from: C:\Users\rohan\HACKATHON
@echo Copying to: Current directory
@echo.

REM Copy the project files
xcopy "C:\Users\rohan\HACKATHON\*" . /E /I /Y /EXCLUDE:exclude.txt >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Files copied successfully
) else (
    echo [ERROR] Failed to copy files
    exit /b 1
)

@echo.
@echo ============================================================================
@echo STEP 2: VERIFY FILES
@echo ============================================================================

if exist Dockerfile (
    echo [OK] Dockerfile - present
) else (
    echo [ERROR] Dockerfile - missing
)

if exist requirements.txt (
    echo [OK] requirements.txt - present
) else (
    echo [ERROR] requirements.txt - missing
)

if exist openenv.yaml (
    echo [OK] openenv.yaml - present
) else (
    echo [ERROR] openenv.yaml - missing
)

if exist environment.py (
    echo [OK] environment.py - present
) else (
    echo [ERROR] environment.py - missing
)

if exist models.py (
    echo [OK] models.py - present
) else (
    echo [ERROR] models.py - missing
)

if exist server\app.py (
    echo [OK] server/app.py - present
) else (
    echo [ERROR] server/app.py - missing
)

@echo.
@echo ============================================================================
@echo STEP 3: PREPARE FOR GIT
@echo ============================================================================

REM Create exclude list
echo .venv > exclude.txt
echo __pycache__ >> exclude.txt
echo *.pyc >> exclude.txt
echo .pytest_cache >> exclude.txt
echo tmp_gradio >> exclude.txt
echo *.log >> exclude.txt
echo .DS_Store >> exclude.txt

REM Remove certain directories
if exist .venv rmdir /s /q .venv 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul

echo [OK] Cleaned up unnecessary files

@echo.
@echo ============================================================================
@echo STEP 4: GIT OPERATIONS (EXECUTE THESE COMMANDS)
@echo ============================================================================
@echo.
@echo Run these commands in PowerShell:
@echo.
@echo 1. Configure git (if first time):
@echo    git config user.name "Your Name"
@echo    git config user.email "your-email@example.com"
@echo.
@echo 2. Add and commit:
@echo    git add .
@echo    git commit -m "Initial OpenEnv AI Safety Review submission"
@echo.
@echo 3. Push to HF:
@echo    git push
@echo    (It will ask for a token - use your HF token from https://huggingface.co/settings/tokens)
@echo.
@echo ============================================================================
@echo STEP 5: WAIT FOR BUILD
@echo ============================================================================
@echo.
@echo After pushing:
@echo 1. Go to: https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%
@echo 2. Watch the "Build logs" tab
@echo 3. Wait for Docker build to complete (usually 5-10 minutes)
@echo 4. Once done, your Space will be live!
@echo.
@echo ============================================================================
@echo YOUR SPACE URL WILL BE
@echo ============================================================================
@echo.
@echo https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%
@echo.
@echo ============================================================================

@echo.
@echo Files are ready in current directory!
@echo Next: Run the git commands above
@echo.
pause
