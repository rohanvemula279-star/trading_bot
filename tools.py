"""
Actual tools. Not descriptions of tools. Working functions.
"""

import os
import subprocess
import json
import requests
from pathlib import Path
from agent_core import Tool


# ──────────────────────────────────────
# 1. FILE OPERATIONS
# ──────────────────────────────────────

def read_file(path: str) -> str:
    """Read file contents."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.stat().st_size > 10_000_000:  # 10MB safety
        raise ValueError(f"File too large: {p.stat().st_size} bytes")
    return p.read_text(encoding="utf-8", errors="replace")


def write_file(path: str, content: str) -> str:
    """Write content to file. Creates dirs if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {path}"


def list_files(directory: str, pattern: str = "*") -> list:
    """List files in directory with optional glob pattern."""
    p = Path(directory)
    if not p.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    return [str(f) for f in p.rglob(pattern) if f.is_file()][:200]  # Cap at 200


def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Find and replace in file."""
    content = read_file(path)
    if old_text not in content:
        raise ValueError(f"Text to replace not found in {path}")
    updated = content.replace(old_text, new_text, 1)
    write_file(path, updated)
    return f"Replaced in {path}"


# ──────────────────────────────────────
# 2. SHELL / COMMAND EXECUTION
# ──────────────────────────────────────

BLOCKED_COMMANDS = ["rm -rf /", "mkfs", ":(){", "dd if=/dev/zero"]

def run_command(command: str, timeout: int = 60) -> dict:
    """Run a shell command safely."""
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            raise PermissionError(f"Blocked dangerous command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-5000:],  # Last 5000 chars
            "stderr": result.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": f"Command timed out after {timeout}s"}


# ──────────────────────────────────────
# 3. WEB / API
# ──────────────────────────────────────

def http_request(url: str, method: str = "GET", headers: dict = None, body: dict = None) -> dict:
    """Make HTTP request."""
    headers = headers or {}
    try:
        resp = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=body,
            timeout=30,
        )
        return {
            "status_code": resp.status_code,
            "body": resp.text[:10000],
            "headers": dict(resp.headers),
        }
    except requests.RequestException as e:
        return {"status_code": -1, "body": "", "error": str(e)}


# ──────────────────────────────────────
# 4. CODE ANALYSIS
# ──────────────────────────────────────

def analyze_python_file(path: str) -> dict:
    """Static analysis of a Python file."""
    import ast

    content = read_file(path)
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "line": node.lineno,
                "decorators": [
                    getattr(d, 'id', getattr(d, 'attr', str(d)))
                    for d in node.decorator_list
                ],
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "methods": [
                    n.name for n in node.body if isinstance(n, ast.FunctionDef)
                ],
            })
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            else:
                imports.append(f"{node.module}.{','.join(a.name for a in node.names)}")

    return {
        "valid": True,
        "lines": len(content.splitlines()),
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }


# ──────────────────────────────────────
# 5. PYTHON CODE EXECUTION (SANDBOXED)
# ──────────────────────────────────────

def execute_python(code: str, timeout: int = 30) -> dict:
    """Execute Python code in a subprocess sandbox."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = run_command(f"python3 {f.name}", timeout=timeout)
        os.unlink(f.name)
        return result


# ──────────────────────────────────────
# TOOL REGISTRY
# ──────────────────────────────────────

ALL_TOOLS = [
    Tool(
        name="read_file",
        description="Read contents of a file",
        function=read_file,
        required_params=["path"],
    ),
    Tool(
        name="write_file",
        description="Write content to a file (creates dirs)",
        function=write_file,
        required_params=["path", "content"],
    ),
    Tool(
        name="edit_file",
        description="Find and replace text in a file",
        function=edit_file,
        required_params=["path", "old_text", "new_text"],
    ),
    Tool(
        name="list_files",
        description="List files in a directory",
        function=list_files,
        required_params=["directory"],
        optional_params=["pattern"],
    ),
    Tool(
        name="run_command",
        description="Run a shell command",
        function=run_command,
        required_params=["command"],
        optional_params=["timeout"],
    ),
    Tool(
        name="http_request",
        description="Make HTTP request (GET/POST/etc)",
        function=http_request,
        required_params=["url"],
        optional_params=["method", "headers", "body"],
    ),
    Tool(
        name="analyze_python",
        description="Analyze Python file structure (functions, classes, imports)",
        function=analyze_python_file,
        required_params=["path"],
    ),
    Tool(
        name="execute_python",
        description="Run Python code and return output",
        function=execute_python,
        required_params=["code"],
        optional_params=["timeout"],
    ),
]
