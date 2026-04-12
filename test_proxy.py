"""
Test script that simulates EXACTLY what the evaluator does.
"""
import os
import sys
import subprocess

FAKE_URL = "http://127.0.0.1:99999/v1"
FAKE_KEY = "sk-test-evaluator-key-12345"
PY = sys.executable
CWD = r"c:\Users\rohan\HACKATHON"

def run_test(name, code, timeout=30):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            [PY, "-c", code],
            capture_output=True, text=True, timeout=timeout,
            cwd=CWD,
            env={
                **os.environ,
                "API_BASE_URL": FAKE_URL,
                "API_KEY": FAKE_KEY,
                "MODEL_NAME": "gpt-4o-mini",
                "SAFETY_TASK": "easy",
                "PERFECT_MODE": "false",
                "PYTHONIOENCODING": "utf-8",
            }
        )
        print(f"  Return code: {result.returncode}")
        if result.stdout.strip():
            print(f"  STDOUT:\n{indent(result.stdout.strip())}")
        if result.stderr.strip():
            # Limit stderr output
            stderr = result.stderr.strip()
            if len(stderr) > 1500:
                stderr = stderr[:1500] + "\n... (truncated)"
            print(f"  STDERR:\n{indent(stderr)}")
        return result
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after {timeout}s - code is HANGING!")
        return None

def indent(text, prefix="    "):
    return "\n".join(prefix + line for line in text.split("\n"))

# ── Test 1: Basic import ──
run_test("Module import (with env vars set)", """
import os, sys
print(f"Python: {sys.version}")
print(f"API_BASE_URL={os.getenv('API_BASE_URL')}")
print(f"API_KEY={os.getenv('API_KEY')}")

# Try import
import inference
print(f"inference.API_BASE_URL={inference.API_BASE_URL}")
print(f"inference.API_KEY={inference.API_KEY}")
print("IMPORT_OK")
""", timeout=15)

# ── Test 2: OpenAI client base_url ──
run_test("OpenAI client base_url check", """
import os
from openai import OpenAI

url = os.environ["API_BASE_URL"]
key = os.environ["API_KEY"]
client = OpenAI(base_url=url, api_key=key)
print(f"Client base_url: {client.base_url}")
print(f"Expected URL: {url}")
base_str = str(client.base_url)
if "127.0.0.1" in base_str and "99999" in base_str:
    print("RESULT=PASS")
else:
    print("RESULT=FAIL")
""", timeout=10)

# ── Test 3: API call reaches the correct URL ──
run_test("API call targets injected URL", """
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=5,
    )
    print(f"UNEXPECTED SUCCESS: {response}")
except Exception as e:
    err = str(e)
    print(f"Error type: {type(e).__name__}")
    print(f"Error: {err[:500]}")
    if "99999" in err or "connect" in err.lower() or "refused" in err.lower():
        print("RESULT=PASS (connection error to our fake URL)")
    else:
        print("RESULT=FAIL (unexpected error type)")
""", timeout=15)

# ── Test 4: Full inference main() flow ──
run_test("Full inference.main() simulation", """
import os, sys, asyncio

# Verify env vars are set
print(f"Pre-import API_BASE_URL: {os.getenv('API_BASE_URL')}")
print(f"Pre-import API_KEY: {os.getenv('API_KEY')}")

import inference

print(f"Post-import API_BASE_URL: {inference.API_BASE_URL}")
print(f"Post-import API_KEY: {inference.API_KEY}")

# Run main
try:
    asyncio.run(inference.main())
except Exception as e:
    print(f"Main error: {type(e).__name__}: {str(e)[:500]}")
except SystemExit as e:
    print(f"SystemExit: {e}")

print("MAIN_COMPLETED")
""", timeout=60)

# ── Test 5: Check if dotenv is interfering ──
run_test("Check dotenv interference", """
import os

# Check if .env file exists and what it contains
env_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        content = f.read()
    print(f".env file exists with {len(content)} bytes:")
    print(content)
    
    # Check for dangerous entries
    for line in content.split("\\n"):
        line = line.strip()
        if line.startswith("API_BASE_URL=") or line.startswith("API_KEY="):
            value = line.split("=", 1)[1].strip()
            if value:
                print(f"WARNING: .env has non-empty {line.split('=')[0]}={value}")
                print("This will override the evaluator's injected values!")
            else:
                print(f"OK: .env has empty {line.split('=')[0]}=")
else:
    print(".env file does not exist (good - evaluator env only)")

print("DOTENV_CHECK_DONE")
""", timeout=10)

# ── Test 6: Check if python-dotenv auto-loads ──
run_test("Check python-dotenv auto-loading", """
import os, sys

# Before any imports, record the env state
pre_url = os.getenv("API_BASE_URL")
pre_key = os.getenv("API_KEY")
print(f"Before import: API_BASE_URL={pre_url}")
print(f"Before import: API_KEY={pre_key}")

# Now import - this might trigger dotenv
import inference

post_url = os.getenv("API_BASE_URL")  
post_key = os.getenv("API_KEY")
print(f"After import: API_BASE_URL={post_url}")
print(f"After import: API_KEY={post_key}")

if pre_url == post_url and pre_key == post_key:
    print("RESULT=PASS (import did not change env vars)")
else:
    print("RESULT=FAIL (import CHANGED env vars!)")
    print(f"URL changed: {pre_url} -> {post_url}")
    print(f"KEY changed: {pre_key} -> {post_key}")
""", timeout=15)

print(f"\n{'='*60}")
print("ALL TESTS COMPLETE")
print(f"{'='*60}")
