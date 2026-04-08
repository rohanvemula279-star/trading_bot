#!/usr/bin/env python
"""
Automated Deployment Script for OpenEnv Hackathon
==================================================

Automates:
1. Git repository initialization and setup
2. GitHub repository creation (requires manual step)
3. Hugging Face Spaces deployment
4. Environment validation

Usage:
    python deploy.py
    # or with specific step:
    python deploy.py --step git      # Just setup git
    python deploy.py --step hf       # Just deploy to HF
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional
import argparse


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def run_command(cmd: str, capture: bool = False) -> tuple[bool, str]:
    """Run a shell command and return success status and output"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, ""
    except Exception as e:
        return False, str(e)


def setup_git():
    """Setup local git repository"""
    print_header("Step 1: Setting up Git Repository")
    
    # Check if git is already initialized
    if Path(".git").exists():
        print_warning("Git repository already initialized")
        return True
    
    # Initialize git
    print_info("Initializing git repository...")
    success, output = run_command("git init", capture=True)
    if success:
        print_success("Git repository initialized")
    else:
        print_error(f"Failed to initialize git: {output}")
        return False
    
    # Configure git
    print_info("Configuring git user...")
    name = input("Enter your name: ").strip()
    email = input("Enter your email: ").strip()
    
    run_command(f'git config user.name "{name}"')
    run_command(f'git config user.email "{email}"')
    print_success(f"Git configured: {name} <{email}>")
    
    # Add all files
    print_info("Adding files to git...")
    success, output = run_command("git add .", capture=True)
    if success:
        print_success("Files staged")
    else:
        print_error(f"Failed to stage files: {output}")
        return False
    
    # Create initial commit
    print_info("Creating initial commit...")
    success, output = run_command(
        'git commit -m "Initial OpenEnv environment setup for hackathon"',
        capture=True
    )
    if success:
        print_success("Initial commit created")
    else:
        print_error(f"Failed to commit: {output}")
        return False
    
    return True


def setup_github_remote():
    """Setup GitHub remote"""
    print_header("Step 2: Setting up GitHub Remote")
    
    print_info("Please create a GitHub repository first:")
    print(f"\n{Colors.CYAN}")
    print("1. Go to https://github.com/new")
    print("2. Create a repository (e.g., 'OpenEnv-Safety-Review')")
    print("3. Make it PUBLIC (required for HF Spaces)")
    print("4. Click 'Create repository'")
    print(f"{Colors.END}")
    
    # Check if remote already exists
    success, output = run_command("git remote -v", capture=True)
    if "origin" in output:
        print_warning("Remote 'origin' already configured")
        print(f"   {output}")
        update = input("Update remote URL? (y/n): ").strip().lower()
        if update != "y":
            return True
    
    github_url = input("\nEnter your GitHub repository URL: ").strip()
    
    if not github_url.startswith("https://") and not github_url.startswith("git@"):
        print_error("Invalid GitHub URL")
        return False
    
    # Add remote
    if "origin" in output:
        print_info("Updating remote...")
        run_command(f"git remote remove origin")
    else:
        print_info("Adding remote...")
    
    success, output = run_command(f"git remote add origin {github_url}", capture=True)
    if success:
        print_success(f"Remote configured: {github_url}")
    else:
        print_error(f"Failed to add remote: {output}")
        return False
    
    # Push to GitHub
    print_info("Pushing to GitHub (main branch)...")
    success, output = run_command("git branch -M main && git push -u origin main", capture=True)
    if success:
        print_success("Code pushed to GitHub")
    else:
        if "Authentication" in output or "permission" in output.lower():
            print_warning("Authentication failed. Please:")
            print("  - Use: git remote set-url origin <URL>")
            print("  - Or set up GitHub SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh")
        else:
            print_warning(f"Push may have partial issues: {output[:100]}")
        return False
    
    return True


def setup_huggingface():
    """Setup Hugging Face authentication"""
    print_header("Step 3: Hugging Face Setup")
    
    # Check if already logged in
    hf_token_file = Path.home() / ".huggingface" / "token"
    if hf_token_file.exists():
        print_success("Hugging Face token already exists")
        return True
    
    print_info("You need a Hugging Face account and token:")
    print(f"{Colors.CYAN}")
    print("1. Create account at https://huggingface.co/join")
    print("2. Get your token: https://huggingface.co/settings/tokens")
    print("3. Create a NEW token with 'write' access")
    print(f"{Colors.END}")
    
    token = input("\nEnter your HF token: ").strip()
    if not token:
        print_error("No token provided")
        return False
    
    # Use huggingface-cli to login
    success, output = run_command(f"huggingface-cli login --token {token}", capture=True)
    if success or "already logged in" in output.lower():
        print_success("Hugging Face authenticated")
        return True
    else:
        # Try manual token save
        token_dir = Path.home() / ".huggingface"
        token_dir.mkdir(parents=True, exist_ok=True)
        with open(token_dir / "token", "w") as f:
            f.write(token)
        print_success("HF token saved manually")
        return True


def deploy_to_huggingface(username: str, space_name: str):
    """Deploy environment to Hugging Face Spaces"""
    print_header("Step 4: Deploying to Hugging Face Spaces")
    
    # Get GitHub repo URL
    success, output = run_command("git remote get-url origin", capture=True)
    if not success:
        print_error("Could not get GitHub URL. Ensure remote 'origin' is configured.")
        return False
    
    github_url = output.strip()
    if not github_url:
        print_error("No GitHub remote configured")
        return False
    
    print_info(f"GitHub URL: {github_url}")
    print_info(f"Space name: {space_name}")
    
    # Check if openenv CLI is available
    success, output = run_command("pip list | findstr openenv", capture=True)
    if not success or "openenv" not in output.lower():
        print_warning("openenv-core not found. Installing...")
        success, output = run_command("pip install openenv-core --upgrade", capture=True)
        if not success:
            print_error(f"Failed to install openenv-core: {output}")
            return False
        print_success("openenv-core installed")
    
    # Deploy using openenv CLI
    repo_id = f"{username}/{space_name}"
    print_info(f"Deploying to: {repo_id}")
    print_info("This may take 1-3 minutes...")
    
    success, output = run_command(f"openenv push --repo-id {repo_id}", capture=True)
    if success:
        hf_space_url = f"https://huggingface.co/spaces/{repo_id}"
        print_success(f"Deployed to Hugging Face Spaces!")
        print(f"{Colors.GREEN}Space URL: {hf_space_url}{Colors.END}")
        return True
    else:
        print_error(f"Deployment failed: {output[:200]}")
        print_warning("Try deploying manually:")
        print(f"  openenv push --repo-id {repo_id}")
        return False


def run_validation():
    """Run validation script"""
    print_header("Step 5: Running Validation")
    
    if not Path("validate_deployment.py").exists():
        print_warning("validate_deployment.py not found")
        return False
    
    print_info("Running validation checks...")
    success, output = run_command("python validate_deployment.py", capture=True)
    
    # Print validation output
    print(output)
    
    return success


def create_deployment_config():
    """Create .deployment.json for tracking"""
    config = {
        "timestamp": str(Path(".").absolute()),
        "status": "in_progress",
        "steps": {
            "git": False,
            "github": False,
            "huggingface": False,
            "validation": False,
        }
    }
    
    with open(".deployment.json", "w") as f:
        json.dump(config, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Deploy OpenEnv environment to Hugging Face Spaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py                    # Run full deployment
  python deploy.py --step git         # Only setup git
  python deploy.py --step hf          # Only deploy to HF
        """
    )
    
    parser.add_argument("--step", choices=["git", "github", "hf", "validation", "all"],
                        default="all", help="Which step to run (default: all)")
    
    args = parser.parse_args()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  OpenEnv Hackathon Deployment Assistant                   ║")
    print("║  Round 1 Deployment - April 8, 2026 Deadline              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    steps_completed = []
    
    try:
        # Step 1: Git
        if args.step in ["all", "git"]:
            if setup_git():
                steps_completed.append("✅ Git initialized")
            else:
                print_error("Git setup failed")
                if args.step != "all":
                    sys.exit(1)
        
        # Step 2: GitHub
        if args.step in ["all", "github"]:
            if setup_github_remote():
                steps_completed.append("✅ GitHub configured")
            else:
                print_warning("GitHub setup had issues")
                if args.step != "all":
                    sys.exit(1)
        
        # Step 3: Hugging Face Auth
        if args.step in ["all", "hf"]:
            if setup_huggingface():
                steps_completed.append("✅ Hugging Face authenticated")
            else:
                print_error("HF authentication failed")
                if args.step != "all":
                    sys.exit(1)
        
        # Step 4: Deploy to HF
        if args.step in ["all", "hf"]:
            username = input("Enter your HF username or organization: ").strip()
            space_name = input("Enter space name (e.g., my-safety-review-env): ").strip()
            
            if deploy_to_huggingface(username, space_name):
                steps_completed.append("✅ Deployed to HF Spaces")
            else:
                print_warning("HF deployment had issues (may need manual setup)")
        
        # Step 5: Validation
        if args.step in ["all", "validation"]:
            if run_validation():
                steps_completed.append("✅ Validation passed")
            else:
                print_warning("Some validation checks failed")
    
    except KeyboardInterrupt:
        print("\n")
        print_warning("Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
    
    # Summary
    print_header("Deployment Summary")
    for step in steps_completed:
        print(step)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("📝 NEXT STEPS:")
    print(f"{Colors.END}")
    print("1. Wait for HF Space to build (check: https://huggingface.co/spaces/your-username/your-space)")
    print("2. Test the deployed space")
    print("3. Submit your Space URL to the hackathon platform")
    print(f"4. {Colors.BOLD}Deadline: April 8, 2026, 11:59 PM IST{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}📚 Resources:{Colors.END}")
    print("  - Deployment Guide: See DEPLOYMENT_GUIDE.md")
    print("  - Validation: python validate_deployment.py")
    print("  - GitHub: https://github.com/meta-pytorch/OpenEnv")


if __name__ == "__main__":
    main()
