#!/usr/bin/env pwsh
<#
.SYNOPSIS
Complete Hugging Face Space Deployment Automation

.DESCRIPTION
Automates the deployment of AI Safety Review Environment to Hugging Face

.NOTES
Before running:
1. Create HF Space: https://huggingface.co/new-space (Docker SDK)
2. Clone it locally
3. Run this script from the cloned space directory

.EXAMPLE
PS> .\Deploy-to-HF.ps1 -HFUsername "your-username" -SpaceName "ai-safety-review"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$HFUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$SpaceName,
    
    [string]$ProjectPath = "C:\Users\rohan\HACKATHON"
)

# Colors for output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Write-Success {
    param([string]$Message)
    Write-Host "${Green}[OK]${Reset} $Message"
}

function Write-Error {
    param([string]$Message)
    Write-Host "${Red}[ERROR]${Reset} $Message"
}

function Write-Info {
    param([string]$Message)
    Write-Host "${Cyan}[INFO]${Reset} $Message"
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "$('='*70)"
    Write-Host "$Title"
    Write-Host "$('='*70)"
    Write-Host ""
}

# Main script
Clear-Host

Write-Host "${Cyan}╔═══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Cyan}║      HUGGING FACE DEPLOYMENT - AI SAFETY REVIEW ENVIRONMENT    ║${Reset}"
Write-Host "${Cyan}╚═══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""

Write-Info "HF Username: $HFUsername"
Write-Info "Space Name: $SpaceName"
Write-Info "Current Directory: $(Get-Location)"
Write-Info "Project Source: $ProjectPath"

Write-Section "STEP 1: Verify Current Directory is Your HF Space"

if (Test-Path ".git") {
    Write-Success "Git repository detected (.git folder found)"
    $remoteUrl = git config --get remote.origin.url 2>$null
    Write-Info "Remote: $remoteUrl"
} else {
    Write-Error "Not in a git repository!"
    Write-Info "Please clone your HF Space first:"
    Write-Info "  git clone https://huggingface.co/spaces/$HFUsername/$SpaceName"
    exit 1
}

Write-Section "STEP 2: Copy Project Files"

# Files to exclude
$exclude = @(
    ".venv",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "tmp_gradio",
    "*.log",
    ".DS_Store",
    ".git",
    "node_modules"
)

Write-Info "Copying files from $ProjectPath..."

try {
    # Copy all files
    Get-ChildItem -Path $ProjectPath -Recurse |
    Where-Object {
        $excluded = $false
        foreach ($pattern in $exclude) {
            if ($_.FullName -like "*$pattern*") {
                $excluded = $true
                break
            }
        }
        -not $excluded
    } |
    ForEach-Object {
        $relativePath = $_.FullName.Substring($ProjectPath.Length + 1)
        $targetPath = Join-Path (Get-Location) $relativePath
        $targetDir = Split-Path $targetPath
        
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        if (-not $_.PSIsContainer) {
            Copy-Item -Path $_.FullName -Destination $targetPath -Force
        }
    }
    
    Write-Success "Files copied successfully"
} catch {
    Write-Error "Failed to copy files: $_"
    exit 1
}

Write-Section "STEP 3: Verify Critical Files"

$criticalFiles = @(
    "Dockerfile",
    "requirements.txt",
    "openenv.yaml",
    "environment.py",
    "models.py",
    "graders.py",
    "server/app.py"
)

$allPresent = $true
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Success "$file"
    } else {
        Write-Error "$file - MISSING!"
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Error "Some critical files are missing!"
    exit 1
}

Write-Section "STEP 4: Clean Up"

$dirsToRemove = @(".venv", "__pycache__", ".pytest_cache", "tmp_gradio")
foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Remove-Item -Path $dir -Recurse -Force 2>$null
        Write-Success "Removed $dir"
    }
}

# Remove log files
Get-ChildItem -Filter "*.log" | Remove-Item -Force 2>$null

Write-Section "STEP 5: Prepare Git"

Write-Info "Creating .gitignore..."
$gitignore = @(
    "# Python",
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "*.so",
    ".venv/",
    "venv/",
    "env/",
    "*.egg-info/",
    "",
    "# Testing",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    "",
    "# IDE",
    ".vscode/",
    ".idea/",
    "*.swp",
    "",
    "# OS",
    ".DS_Store",
    "Thumbs.db",
    "",
    "# Logs",
    "*.log",
    "",
    "# Temporary",
    "tmp_gradio/",
    ".env.local"
)

Set-Content -Path ".gitignore" -Value $gitignore -Encoding UTF8
Write-Success ".gitignore created"

Write-Section "STEP 6: Git Configuration & Commit"

Write-Info "Checking git configuration..."

$gitName = git config user.name 2>$null
$gitEmail = git config user.email 2>$null

if (-not $gitName -or -not $gitEmail) {
    Write-Info "Git user not configured. Configuring..."
    git config user.name "OpenEnv Deployer" 2>$null
    git config user.email "deployer@openenv.local" 2>$null
    Write-Success "Git configured"
} else {
    Write-Success "Git already configured: $gitName <$gitEmail>"
}

Write-Info "Staging files..."
git add . 2>$null
Write-Success "Files staged"

Write-Info "Creating commit..."
git commit -m "Deploy: AI Safety Review Environment to HF Space" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Commit created"
} else {
    Write-Info "Nothing new to commit (or commit already exists)"
}

Write-Section "STEP 7: Push to Hugging Face"

Write-Host "${Yellow}IMPORTANT: You need to push to Hugging Face${Reset}"
Write-Host ""
Write-Info "Generate or copy your HF token from: https://huggingface.co/settings/tokens"
Write-Info "When prompted, enter your token as the password"
Write-Host ""

Write-Host "${Cyan}Running: git push${Reset}"
Write-Host ""

git push

if ($LASTEXITCODE -eq 0) {
    Write-Success "Successfully pushed to Hugging Face!"
} else {
    Write-Error "Push failed. Check the error above."
    Write-Info "Common solution: Ensure you have a valid HF token"
    exit 1
}

Write-Section "DEPLOYMENT COMPLETE!"

Write-Host "${Green}✓ Your Space is being built on Hugging Face!${Reset}"
Write-Host ""
Write-Host "${Cyan}Your Space URL:${Reset}"
Write-Host "  ${Yellow}https://huggingface.co/spaces/$HFUsername/$SpaceName${Reset}"
Write-Host ""
Write-Host "${Cyan}Next Steps:${Reset}"
Write-Host "  1. Visit the URL above"
Write-Host "  2. Go to 'Build logs' tab to watch the build progress"
Write-Host "  3. Wait 5-15 minutes for Docker build to complete"
Write-Host "  4. Once done, your Space will be LIVE!"
Write-Host ""
Write-Host "${Cyan}Configuration (Optional - if using API):${Reset}"
Write-Host "  1. Click 'Settings' on your Space"
Write-Host "  2. Add Variables and Secrets:"
Write-Host "     - API_KEY: your-openai-api-key"
Write-Host "     - HF_TOKEN: your-huggingface-token"
Write-Host "     - MODEL_NAME: gpt-4o-mini"
Write-Host ""
Write-Host "${Green}Done!${Reset}"
Write-Host ""
