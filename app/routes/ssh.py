"""
SSH Access System - Direct connection to Replit apps
Enables remote access to Replit workspaces via SSH
"""
import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings


router = APIRouter(prefix="/api/ssh", tags=["ssh"])


# ============================================================================
# SSH Key Management
# ============================================================================

class SSHKeyGen(BaseModel):
    """Generate SSH key request"""
    key_name: Optional[str] = "repeditor"
    key_type: str = "ed25519"


class SSHKeyAdd(BaseModel):
    """Add SSH key to Replit account"""
    public_key: str
    title: str = "RepEditor Access"


class ReplConnect(BaseModel):
    """Connect to Repl via SSH"""
    repl_slug: str
    repl_owner: str


@router.post("/keygen")
async def generate_ssh_key(req: SSHKeyGen):
    """Generate SSH keypair for Replit access"""
    try:
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir(parents=True, exist_ok=True)
        
        key_name = req.key_name
        private_key_path = ssh_dir / key_name
        public_key_path = ssh_dir / f'{key_name}.pub'
        
        # Generate ED25519 key (modern, secure)
        result = subprocess.run(
            [
                'ssh-keygen',
                '-t', req.key_type,
                '-f', str(private_key_path),
                '-N', '',  # No passphrase
                '-C', 'repeditor@replit'
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise Exception(f"SSH key generation failed: {result.stderr}")
        
        # Read public key
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
        
        return JSONResponse({
            "ok": True,
            "public_key": public_key,
            "private_key_path": str(private_key_path),
            "instructions": "Add this public key to your Replit account at: https://replit.com/account#ssh-keys"
        })
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="SSH key generation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def list_ssh_keys():
    """List SSH keys in user's .ssh directory"""
    try:
        ssh_dir = Path.home() / '.ssh'
        if not ssh_dir.exists():
            return JSONResponse({"keys": []})
        
        keys = []
        for key_file in ssh_dir.glob('*.pub'):
            try:
                with open(key_file, 'r') as f:
                    content = f.read().strip()
                    keys.append({
                        'name': key_file.stem,
                        'path': str(key_file),
                        'content': content,
                        'type': 'public'
                    })
            except Exception:
                pass
        
        return JSONResponse({"keys": keys})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Replit SSH Connection
# ============================================================================

@router.post("/connect")
async def connect_to_repl(req: ReplConnect):
    """
    Get SSH connection details for a Replit app
    
    Note: User must have SSH keys configured in their Replit account.
    See: https://replit.com/account#ssh-keys
    """
    try:
        # Construct SSH host for Replit
        # Format: <repl-slug>.<repl-owner>.repl.co
        ssh_host = f"{req.repl_slug}.{req.repl_owner}.repl.co"
        
        # SSH command
        ssh_command = f"ssh {ssh_host}"
        
        return JSONResponse({
            "ok": True,
            "ssh_host": ssh_host,
            "ssh_command": ssh_command,
            "port": 22,
            "instructions": [
                "1. Ensure your SSH key is added to Replit: https://replit.com/account#ssh-keys",
                "2. Run the command in your terminal:",
                f"   {ssh_command}",
                "3. Or configure VSCode/Cursor for remote SSH editing"
            ]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exec")
async def exec_ssh_command(
    repl_slug: str,
    repl_owner: str,
    command: str
):
    """
    Execute command on remote Repl via SSH
    
    WARNING: This requires SSH keys to be configured and working.
    """
    try:
        ssh_host = f"{repl_slug}.{repl_owner}.repl.co"
        
        # Execute command via SSH
        result = subprocess.run(
            ['ssh', '-o', 'StrictHostKeyChecking=no', ssh_host, command],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return JSONResponse({
            "ok": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Command timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repls")
async def list_replit_apps():
    """
    List user's Replit apps
    
    Note: This uses the Replit GraphQL API with the user's session token.
    For now, this is a placeholder - proper implementation requires:
    1. User's Replit session token (connect.sid cookie)
    2. GraphQL query to https://replit.com/graphql
    """
    
    # Check if user has REPL environment variables (running on Replit)
    if settings.REPL_OWNER and settings.REPL_SLUG:
        current_workspace = {
            "id": settings.REPL_ID or "current",
            "name": "Current Workspace",
            "slug": settings.REPL_SLUG,
            "owner": settings.REPL_OWNER,
            "url": f"https://replit.com/@{settings.REPL_OWNER}/{settings.REPL_SLUG}",
            "ssh_host": f"{settings.REPL_SLUG}.{settings.REPL_OWNER}.repl.co",
            "is_current": True
        }
        
        return JSONResponse({
            "ok": True,
            "repls": [current_workspace],
            "note": "To list all your Repls, you need to authenticate with Replit GraphQL API"
        })
    
    return JSONResponse({
        "ok": True,
        "repls": [],
        "note": "Not running on Replit or Replit API token not configured"
    })


# ============================================================================
# SSH File Operations
# ============================================================================

@router.post("/browse")
async def browse_repl_files(
    repl_slug: str,
    repl_owner: str,
    path: str = "/home/runner"
):
    """Browse files in remote Repl via SSH"""
    try:
        ssh_host = f"{repl_slug}.{repl_owner}.repl.co"
        
        # List files with details
        result = subprocess.run(
            ['ssh', '-o', 'StrictHostKeyChecking=no', ssh_host, 
             f'ls -lAh --color=never {path}'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to list files: {result.stderr}")
        
        return JSONResponse({
            "ok": True,
            "path": path,
            "output": result.stdout
        })
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Browse timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read")
async def read_repl_file(
    repl_slug: str,
    repl_owner: str,
    file_path: str
):
    """Read file content from remote Repl via SSH"""
    try:
        ssh_host = f"{repl_slug}.{repl_owner}.repl.co"
        
        # Read file via SSH
        result = subprocess.run(
            ['ssh', '-o', 'StrictHostKeyChecking=no', ssh_host, 
             f'cat {file_path}'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to read file: {result.stderr}")
        
        return JSONResponse({
            "ok": True,
            "path": file_path,
            "content": result.stdout
        })
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Read timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
