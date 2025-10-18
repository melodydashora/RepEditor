"""Repository management - clone, browse, git operations"""

from fastapi import APIRouter, HTTPException, Depends, Form, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import subprocess
from pathlib import Path
import os

from app.routes.auth import get_current_user
from app.models.auth import AuthSession

router = APIRouter(prefix="/api/repos", tags=["repositories"])

# Configuration
BASE_DIR = Path(os.getenv("BASE_DIR", "/home/runner/workspace")).resolve()
CLONE_ROOT = (BASE_DIR / "repos").resolve()
CLONE_ROOT.mkdir(parents=True, exist_ok=True)


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> str:
    """Execute git command safely"""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Command failed: {' '.join(cmd)}\n{result.stderr}"
            )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Command timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SelectRepoRequest(BaseModel):
    """Select and clone repository"""
    full_name: str  # e.g. "username/repo"
    branch: Optional[str] = None


class GitConfigRequest(BaseModel):
    """Git user configuration"""
    name: str
    email: str


class GitCommitRequest(BaseModel):
    """Git commit"""
    message: str
    paths: str = "."


class GitPushRequest(BaseModel):
    """Git push"""
    remote: str = "origin"
    branch: str = "HEAD"


@router.post("/select")
async def select_repo(
    request: SelectRepoRequest,
    session: AuthSession = Depends(get_current_user)
):
    """
    Select and clone a GitHub repository to local workspace
    
    - Clones repo if not exists
    - Fetches latest if already cloned
    - Sets up git remote with OAuth token
    - Checks out specified branch
    """
    if not session.github_token:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    # Parse owner/repo
    parts = request.full_name.split("/", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid repo format (use owner/repo)")
    
    owner, repo = parts
    target = (CLONE_ROOT / owner / repo).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Build authenticated clone URL
    remote_url = f"https://oauth2:{session.github_token}@github.com/{owner}/{repo}.git"
    
    try:
        # Clone or fetch
        if target.exists() and (target / ".git").exists():
            # Repo exists - update remote and fetch
            run_command(["git", "remote", "set-url", "origin", remote_url], cwd=target)
            run_command(["git", "fetch", "--all", "--prune"], cwd=target)
        else:
            # Clone with shallow history
            run_command(["git", "clone", "--depth", "1", remote_url, str(target)])
        
        # Determine branch
        branch = request.branch
        if not branch:
            # Get default branch from GitHub API or use main
            branch = "main"
        
        # Checkout branch
        run_command(["git", "checkout", branch], cwd=target)
        
        # Store repo path in session (update in database if needed)
        # For now, return the path - UI will use it for subsequent calls
        
        return {
            "ok": True,
            "path": str(target),
            "full_name": request.full_name,
            "branch": branch,
            "message": f"Repository {request.full_name} ready"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone repo: {str(e)}")


@router.get("/tree")
async def get_repo_tree(
    repo_path: str = Query(..., description="Full path to repository"),
    session: AuthSession = Depends(get_current_user),
    max_entries: int = Query(8000, le=10000)
):
    """
    Get file tree for a repository
    
    Returns list of all files and directories with:
    - Relative path
    - Name
    - Type (file/dir)
    - Size (bytes, for files only)
    """
    root = Path(repo_path).resolve()
    
    # Security: ensure path is within CLONE_ROOT
    if CLONE_ROOT not in root.parents and root != CLONE_ROOT:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not root.exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Build tree
    items = []
    count = 0
    
    for p in sorted(root.rglob("*")):
        # Skip .git internals
        if ".git" in p.parts:
            continue
        
        rel_path = p.relative_to(root)
        item = {
            "path": str(rel_path),
            "name": p.name,
            "kind": "dir" if p.is_dir() else "file",
            "size": None if p.is_dir() else p.stat().st_size
        }
        items.append(item)
        
        count += 1
        if count >= max_entries:
            break
    
    return {
        "root": str(root),
        "count": len(items),
        "items": items
    }


@router.get("/file")
async def get_file_content(
    repo_path: str = Query(..., description="Repository root path"),
    file_path: str = Query(..., description="Relative file path"),
    session: AuthSession = Depends(get_current_user)
):
    """
    Read file content from repository
    
    Returns plain text content or [binary file] for binary files
    """
    root = Path(repo_path).resolve()
    
    # Security checks
    if CLONE_ROOT not in root.parents and root != CLONE_ROOT:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file = (root / file_path).resolve()
    
    # Ensure file is within repo
    if root not in file.parents and file != root:
        raise HTTPException(status_code=403, detail="Path escapes repository")
    
    if not file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    
    try:
        content = file.read_text(encoding="utf-8")
        return PlainTextResponse(content)
    except UnicodeDecodeError:
        return PlainTextResponse("[binary file]")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/git/config")
async def git_config(
    request: GitConfigRequest,
    repo_path: str = Form(...),
    session: AuthSession = Depends(get_current_user)
):
    """Configure git user name and email for repository"""
    root = Path(repo_path).resolve()
    
    if CLONE_ROOT not in root.parents and root != CLONE_ROOT:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not root.exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    
    run_command(["git", "config", "user.name", request.name], cwd=root)
    run_command(["git", "config", "user.email", request.email], cwd=root)
    
    return {"ok": True, "message": "Git config updated"}


@router.post("/git/commit")
async def git_commit(
    request: GitCommitRequest,
    repo_path: str = Form(...),
    session: AuthSession = Depends(get_current_user)
):
    """Stage and commit changes"""
    root = Path(repo_path).resolve()
    
    if CLONE_ROOT not in root.parents and root != CLONE_ROOT:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not root.exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Stage files
    run_command(["git", "add", request.paths], cwd=root)
    
    # Commit with sign-off
    run_command(["git", "commit", "-s", "-m", request.message], cwd=root)
    
    return {"ok": True, "message": "Changes committed"}


@router.post("/git/push")
async def git_push(
    request: GitPushRequest,
    repo_path: str = Form(...),
    session: AuthSession = Depends(get_current_user)
):
    """Push commits to remote"""
    root = Path(repo_path).resolve()
    
    if CLONE_ROOT not in root.parents and root != CLONE_ROOT:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not root.exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Push to remote
    run_command(["git", "push", request.remote, request.branch], cwd=root)
    
    return {"ok": True, "message": "Changes pushed to remote"}


@router.get("/git/status")
async def git_status(
    repo_path: str = Query(...),
    session: AuthSession = Depends(get_current_user)
):
    """Get git status for repository"""
    root = Path(repo_path).resolve()
    
    if CLONE_ROOT not in root.parents and root != CLONE_ROOT:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not root.exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    
    status = run_command(["git", "status", "--short"], cwd=root)
    branch = run_command(["git", "branch", "--show-current"], cwd=root).strip()
    
    return {
        "branch": branch,
        "status": status,
        "has_changes": bool(status.strip())
    }
