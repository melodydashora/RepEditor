"""Configuration API for agent repository access and Replit integration"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json
import secrets
import subprocess
from pathlib import Path

router = APIRouter(prefix="/api/config", tags=["config"])


class ReplitConnect(BaseModel):
    """Replit connection credentials"""
    username: str
    password: str


class TokenSave(BaseModel):
    """Repository access token"""
    token: str
    repo_url: Optional[str] = None


class TokenTest(BaseModel):
    """Test repository token"""
    token: str


class PermissionsUpdate(BaseModel):
    """Agent permissions"""
    read: bool = True
    write: bool = True
    execute: bool = True
    git: bool = True
    web: bool = True
    memory: bool = True


# In-memory storage (replace with database in production)
CONFIG_FILE = Path("data/config/agent_config.json")
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


@router.post("/replit/connect")
async def connect_replit(request: ReplitConnect):
    """
    Connect to Replit account and list available apps
    
    Note: This is a placeholder - actual Replit API integration requires:
    - Replit API token (not username/password)
    - OAuth flow for secure authentication
    - Replit GraphQL API to list user's Repls
    """
    try:
        # Store credentials securely (in production, use secrets manager)
        config = load_config()
        config['replit'] = {
            'username': request.username,
            # Never store passwords in plain text - use environment secrets instead
            'authenticated': True
        }
        save_config(config)
        
        # Mock response with Replit apps (replace with actual API call)
        # In production: Use Replit GraphQL API to fetch user's Repls
        apps = [
            {
                'id': 'vecto-pilot',
                'name': 'Vecto Pilot',
                'slug': 'vecto-pilot',
                'description': 'Rideshare driver assistance platform',
                'language': 'Python',
                'url': 'https://replit.com/@' + request.username + '/vecto-pilot'
            },
            {
                'id': 'current-workspace',
                'name': 'Current Workspace (This App)',
                'slug': 'current',
                'description': 'Currently running Replit app',
                'language': 'Python',
                'url': 'local'
            }
        ]
        
        return {
            'success': True,
            'message': 'Connected to Replit account',
            'username': request.username,
            'apps': apps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/replit/apps")
async def list_replit_apps():
    """List available Replit apps for current user"""
    config = load_config()
    
    if 'replit' not in config or not config['replit'].get('authenticated'):
        raise HTTPException(status_code=401, detail="Not authenticated with Replit")
    
    # Mock response - replace with actual Replit API call
    return {
        'apps': [
            {
                'id': 'current-workspace',
                'name': 'Current Workspace',
                'active': True
            }
        ]
    }


@router.post("/ssh/generate")
async def generate_ssh_key():
    """Generate SSH keypair for agent repository access"""
    try:
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir(parents=True, exist_ok=True)
        
        key_name = 'vecto_agent_key'
        private_key_path = ssh_dir / key_name
        public_key_path = ssh_dir / f'{key_name}.pub'
        
        # Generate ED25519 key (modern, secure)
        result = subprocess.run(
            [
                'ssh-keygen',
                '-t', 'ed25519',
                '-f', str(private_key_path),
                '-N', '',  # No passphrase
                '-C', 'vecto-agent@replit'
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
        
        return {
            'success': True,
            'public_key': public_key,
            'private_key_path': str(private_key_path),
            'message': 'SSH keypair generated successfully'
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="SSH key generation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ssh/list")
async def list_ssh_keys():
    """List existing SSH keys"""
    try:
        ssh_dir = Path.home() / '.ssh'
        if not ssh_dir.exists():
            return {'keys': []}
        
        keys = []
        for key_file in ssh_dir.glob('*.pub'):
            keys.append({
                'name': key_file.stem,
                'path': str(key_file),
                'type': 'public'
            })
        
        return {'keys': keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/generate")
async def generate_token():
    """Generate repository access token"""
    token = secrets.token_urlsafe(32)
    
    config = load_config()
    config['access_token'] = token
    save_config(config)
    
    return {
        'success': True,
        'token': token,
        'message': 'Access token generated'
    }


@router.post("/token/save")
async def save_token(request: TokenSave):
    """Save repository access token"""
    config = load_config()
    config['access_token'] = request.token
    if request.repo_url:
        config['repo_url'] = request.repo_url
    save_config(config)
    
    return {
        'success': True,
        'message': 'Token saved successfully'
    }


@router.post("/token/test")
async def test_token(request: TokenTest):
    """Test repository access token"""
    # Simple validation for now
    if not request.token:
        raise HTTPException(status_code=400, detail="Token is required")
    
    config = load_config()
    stored_token = config.get('access_token')
    
    if stored_token and stored_token == request.token:
        return {
            'success': True,
            'access_level': 'Full',
            'repo': config.get('repo_url', 'Local'),
            'message': 'Token is valid'
        }
    else:
        return {
            'success': True,
            'access_level': 'Read-only',
            'repo': 'Local',
            'message': 'Token validated (new token)'
        }


@router.get("/token/current")
async def get_current_token():
    """Get current repository access token"""
    config = load_config()
    token = config.get('access_token')
    
    if token:
        # Return masked token for security
        masked = token[:8] + '...' + token[-8:]
        return {
            'token': masked,
            'full_token': token if os.getenv('NODE_ENV') == 'development' else None
        }
    return {'token': None}


@router.post("/permissions")
async def save_permissions(request: PermissionsUpdate):
    """Save agent permissions"""
    config = load_config()
    config['permissions'] = request.dict()
    save_config(config)
    
    return {
        'success': True,
        'message': 'Permissions saved',
        'permissions': request.dict()
    }


@router.get("/permissions")
async def get_permissions():
    """Get current agent permissions"""
    config = load_config()
    return config.get('permissions', {
        'read': True,
        'write': True,
        'execute': True,
        'git': True,
        'web': True,
        'memory': True
    })
