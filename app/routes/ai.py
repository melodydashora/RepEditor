"""
AI Autofix System - GPT-5 Planning + Codex Patching
Remote repository fixing with GitHub token-based authentication
"""
import os
import json
import tempfile
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import httpx
from openai import OpenAI

from app.core.config import settings


router = APIRouter(prefix="/api/ai", tags=["ai"])


# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


# Model configuration
REASONER_MODEL = os.getenv("SDK_MODEL", "gpt-5")  # GPT-5 Thinking
CODE_MODEL = os.getenv("SDK_CODE_MODEL", "gpt-5-codex")  # Codex for patches


# ============================================================================
# Helper Functions
# ============================================================================

def run(cmd: List[str], cwd: Optional[Path] = None) -> str:
    """Execute shell command and return output"""
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True
    )
    if p.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Command failed: {' '.join(cmd)}\n{p.stderr.strip()}"
        )
    return p.stdout


def git_clone(repo_full: str, token: str, branch: Optional[str] = None) -> Path:
    """Clone repository with GitHub token authentication"""
    owner, name = repo_full.split("/", 1)
    tmp = Path(tempfile.mkdtemp(prefix="ai-repo-"))
    remote = f"https://oauth2:{token}@github.com/{owner}/{name}.git"
    
    run(["git", "clone", "--filter=blob:none", "--no-tags", remote, str(tmp)])
    
    if branch:
        run(["git", "checkout", branch], cwd=tmp)
    
    # Configure git identity
    run(["git", "config", "user.name", os.getenv("GIT_AUTHOR_NAME", "RepEditor AI")], cwd=tmp)
    run(["git", "config", "user.email", os.getenv("GIT_AUTHOR_EMAIL", "ai@repeditor.dev")], cwd=tmp)
    
    return tmp


def build_tree(root: Path, max_entries: int = 8000) -> List[Dict[str, Any]]:
    """Build file tree structure from repository"""
    out, n = [], 0
    for p in sorted(root.rglob("*")):
        if ".git" in p.parts:
            continue
        rel = p.relative_to(root)
        out.append({
            "path": str(rel),
            "kind": "dir" if p.is_dir() else "file",
            "size": None if p.is_dir() else p.stat().st_size
        })
        n += 1
        if n >= max_entries:
            break
    return out


def git_new_branch(root: Path, base_branch: Optional[str], slug: str) -> str:
    """Create new branch for changes"""
    if base_branch:
        run(["git", "checkout", base_branch], cwd=root)
    br = f"repeditor/{slug}"
    run(["git", "checkout", "-b", br], cwd=root)
    return br


def apply_unified_diff(root: Path, diff_text: str):
    """Apply unified diff to repository"""
    tmp = root / f".repeditor_patch_{uuid.uuid4().hex}.diff"
    tmp.write_text(diff_text, encoding="utf-8")
    
    try:
        run(["git", "apply", "--index", str(tmp)], cwd=root)
    except HTTPException:
        # Fallback to patch command
        run(["patch", "-p0", "-i", str(tmp)], cwd=root)
        run(["git", "add", "-A"], cwd=root)
    finally:
        tmp.unlink(missing_ok=True)


def git_commit_push(root: Path, branch: str, message: str):
    """Commit and push changes"""
    run(["git", "commit", "-s", "-m", message], cwd=root)
    run(["git", "push", "origin", branch], cwd=root)


async def gh_get_default_branch(token: str, repo_full: str) -> str:
    """Get default branch from GitHub API"""
    async with httpx.AsyncClient() as http:
        r = await http.get(
            f"https://api.github.com/repos/{repo_full}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
        r.raise_for_status()
        return r.json().get("default_branch") or "main"


async def gh_open_pr(
    token: str,
    repo_full: str,
    head_branch: str,
    base_branch: str,
    title: str,
    body: str
) -> str:
    """Open pull request on GitHub"""
    async with httpx.AsyncClient() as http:
        r = await http.post(
            f"https://api.github.com/repos/{repo_full}/pulls",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            },
            json={
                "title": title,
                "head": head_branch,
                "base": base_branch,
                "body": body
            }
        )
        r.raise_for_status()
        return r.json()["html_url"]


# ============================================================================
# AI Prompts
# ============================================================================

PLAN_SYS = """You are the RepEditor AI Assistant (GPT-5).
You are given a repository tree and a goal. Produce a crisp plan:
- bullet steps
- targeted files
- risks/validation checks
Respond as tight JSON with keys: plan[], files[], risks[], tests[]."""


DIFF_SYS = """You are gpt-5-codex.
Generate a UNIFIED DIFF that applies cleanly (git apply --index).
Constraints:
- Output ONLY the diff (no prose).
- Use correct paths relative to repo root.
- Keep changes minimal and focused on the task."""


def chat_json(model: str, system: str, user: str) -> Dict[str, Any]:
    """Call OpenAI and parse JSON response"""
    resp = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2
    )
    txt = resp.choices[0].message.content
    try:
        return json.loads(txt)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Model did not return JSON: {txt[:500]}"
        )


def chat_text(model: str, system: str, user: str) -> str:
    """Call OpenAI and return text response"""
    resp = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2
    )
    return resp.choices[0].message.content or ""


# ============================================================================
# Request Models
# ============================================================================

class PlanReq(BaseModel):
    repo: str
    branch: Optional[str] = None
    goal: str
    sample_paths: Optional[List[str]] = None


class DiffReq(BaseModel):
    repo: str
    branch: Optional[str] = None
    goal: str
    context_files: List[str]
    patch_mode: str = "unified"
    dry_run: bool = True


class ApplyReq(BaseModel):
    repo: str
    base_branch: Optional[str] = None
    diff: str
    commit_message: str = "chore(repeditor): automated fix"
    create_pr: bool = True
    pr_title: Optional[str] = None
    pr_body: Optional[str] = None


class AutoReq(BaseModel):
    repo: str
    branch: Optional[str] = None
    goal: str
    context_files: Optional[List[str]] = None
    create_pr: bool = True


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/plan")
async def ai_plan(req: PlanReq, x_gh_token: str = Header(None, alias="X-GH-Token")):
    """Generate AI plan for repository fixes"""
    if not x_gh_token:
        raise HTTPException(status_code=401, detail="Missing X-GH-Token header")
    
    base = await gh_get_default_branch(x_gh_token, req.repo) if not req.branch else req.branch
    root = git_clone(req.repo, x_gh_token, base)
    
    try:
        # Build tree + optional file samples
        tree = build_tree(root)
        samples = {}
        
        for p in (req.sample_paths or [])[:20]:
            fp = root / p
            if fp.exists() and fp.is_file():
                try:
                    samples[p] = fp.read_text(encoding="utf-8")[:65536]
                except Exception:
                    pass
        
        user_msg = json.dumps({
            "branch": base,
            "tree": tree[:4000],
            "goal": req.goal,
            "samples": samples
        }, ensure_ascii=False)
        
        out = chat_json(REASONER_MODEL, PLAN_SYS, user_msg)
        
        return JSONResponse({"ok": True, "plan": out, "branch": base})
    
    finally:
        shutil.rmtree(root, ignore_errors=True)


@router.post("/diff")
async def ai_diff(req: DiffReq, x_gh_token: str = Header(None, alias="X-GH-Token")):
    """Generate unified diff for repository fixes"""
    if not x_gh_token:
        raise HTTPException(status_code=401, detail="Missing X-GH-Token header")
    
    base = await gh_get_default_branch(x_gh_token, req.repo) if not req.branch else req.branch
    root = git_clone(req.repo, x_gh_token, base)
    
    try:
        # Load context files
        ctx_blobs = {}
        for p in req.context_files[:50]:
            fp = root / p
            if fp.exists() and fp.is_file():
                try:
                    ctx_blobs[p] = fp.read_text(encoding="utf-8")[:200000]
                except Exception:
                    pass
        
        prompt = f"""GOAL:
{req.goal}

CURRENT FILES (name -> content, truncated):
{json.dumps(ctx_blobs, ensure_ascii=False)[:300000]}"""
        
        diff = chat_text(CODE_MODEL, DIFF_SYS, prompt)
        
        if not diff.lstrip().startswith(("diff ", "--- ")):
            raise HTTPException(status_code=500, detail="Model did not return a unified diff.")
        
        if not req.dry_run:
            slug = uuid.uuid4().hex[:8]
            branch = git_new_branch(root, base, slug)
            apply_unified_diff(root, diff)
            git_commit_push(root, branch, f"chore(repeditor): {req.goal[:80]}")
        
        return PlainTextResponse(diff)
    
    finally:
        shutil.rmtree(root, ignore_errors=True)


@router.post("/apply")
async def ai_apply(req: ApplyReq, x_gh_token: str = Header(None, alias="X-GH-Token")):
    """Apply diff and create pull request"""
    if not x_gh_token:
        raise HTTPException(status_code=401, detail="Missing X-GH-Token header")
    
    base = await gh_get_default_branch(x_gh_token, req.repo) if not req.base_branch else req.base_branch
    root = git_clone(req.repo, x_gh_token, base)
    
    try:
        branch = git_new_branch(root, base, uuid.uuid4().hex[:8])
        apply_unified_diff(root, req.diff)
        git_commit_push(root, branch, req.commit_message)
        
        pr_url = None
        if req.create_pr:
            pr_url = await gh_open_pr(
                x_gh_token,
                req.repo,
                branch,
                base,
                req.pr_title or req.commit_message,
                req.pr_body or "Automated change by RepEditor AI Assistant."
            )
        
        return JSONResponse({
            "ok": True,
            "branch": branch,
            "base": base,
            "pr_url": pr_url
        })
    
    finally:
        shutil.rmtree(root, ignore_errors=True)


@router.post("/autofix")
async def ai_autofix(req: AutoReq, x_gh_token: str = Header(None, alias="X-GH-Token")):
    """One-click autofix: plan -> diff -> apply -> PR"""
    if not x_gh_token:
        raise HTTPException(status_code=401, detail="Missing X-GH-Token header")
    
    # Step 1: Generate plan
    plan_resp = await ai_plan(
        PlanReq(
            repo=req.repo,
            branch=req.branch,
            goal=req.goal,
            sample_paths=req.context_files or []
        ),
        x_gh_token
    )
    plan_data = json.loads(plan_resp.body.decode())
    base = plan_data["branch"]
    
    # Step 2: Generate diff
    files_from_plan = plan_data.get("plan", {}).get("files", [])[:12]
    diff_resp = await ai_diff(
        DiffReq(
            repo=req.repo,
            branch=base,
            goal=req.goal,
            context_files=req.context_files or files_from_plan,
            dry_run=True
        ),
        x_gh_token
    )
    diff_txt = diff_resp.body.decode()
    
    # Step 3: Apply and create PR
    apply_resp = await ai_apply(
        ApplyReq(
            repo=req.repo,
            base_branch=base,
            diff=diff_txt,
            commit_message=f"chore(repeditor): {req.goal[:80]}",
            create_pr=req.create_pr
        ),
        x_gh_token
    )
    
    return apply_resp


@router.get("/tree")
async def ai_tree(
    repo: str,
    branch: Optional[str] = None,
    x_gh_token: str = Header(None, alias="X-GH-Token")
):
    """Browse repository file tree"""
    if not x_gh_token:
        raise HTTPException(status_code=401, detail="Missing X-GH-Token header")
    
    base = await gh_get_default_branch(x_gh_token, repo) if not branch else branch
    root = git_clone(repo, x_gh_token, base)
    
    try:
        return JSONResponse({
            "repo": repo,
            "branch": base,
            "items": build_tree(root)
        })
    finally:
        shutil.rmtree(root, ignore_errors=True)


@router.get("/file")
async def ai_file(
    repo: str,
    path: str,
    branch: Optional[str] = None,
    x_gh_token: str = Header(None, alias="X-GH-Token")
):
    """Read file content from repository"""
    if not x_gh_token:
        raise HTTPException(status_code=401, detail="Missing X-GH-Token header")
    
    base = await gh_get_default_branch(x_gh_token, repo) if not branch else branch
    root = git_clone(repo, x_gh_token, base)
    
    try:
        fp = (root / path).resolve()
        if root not in fp.parents and fp != root:
            raise HTTPException(status_code=400, detail="Path escapes repository")
        if not fp.exists() or not fp.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        return PlainTextResponse(fp.read_text(encoding="utf-8"))
    finally:
        shutil.rmtree(root, ignore_errors=True)
