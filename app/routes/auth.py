"""
Authentication routes with GitHub OAuth and username/password support
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from authlib.integrations.starlette_client import OAuth
import httpx

from app.core.config import settings, get_db
from app.models.auth import User, AuthSession


router = APIRouter(prefix="/api/auth", tags=["authentication"])


oauth = OAuth()
oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user repo"},
)


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class GitHubTokenRequest(BaseModel):
    token: str


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password


def generate_session_token() -> str:
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)


def create_session(db: Session, user_id: int, github_token: Optional[str] = None) -> AuthSession:
    """Create a new auth session for a user"""
    session_token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    session = AuthSession(
        user_id=user_id,
        session_token=session_token,
        github_token=github_token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


async def get_current_session(
    request: Request,
    db: Session = Depends(get_db)
) -> tuple[User, AuthSession]:
    """Dependency to get the current authenticated user and session"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.replace("Bearer ", "")
    
    session = db.query(AuthSession).filter(
        AuthSession.session_token == token,
        AuthSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    session.last_activity = datetime.utcnow()
    db.commit()
    
    return user, session


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user"""
    user, _ = await get_current_session(request, db)
    return user


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user with username/password"""
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    session = create_session(db, user.id)
    
    return {
        "ok": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "session_token": session.session_token,
        "expires_at": session.expires_at.isoformat()
    }


@router.post("/login")
async def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with username/password"""
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    session = create_session(db, user.id)
    
    return {
        "ok": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "github_username": user.github_username
        },
        "session_token": session.session_token,
        "expires_at": session.expires_at.isoformat()
    }


@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Logout and invalidate session"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = auth_header.replace("Bearer ", "")
    
    session = db.query(AuthSession).filter(
        AuthSession.session_token == token
    ).first()
    
    if session:
        db.delete(session)
        db.commit()
    
    return {"ok": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user)
):
    """Get current user info"""
    return {
        "ok": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "github_username": user.github_username,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.get("/github/start")
async def github_oauth_start(request: Request):
    """Initiate GitHub OAuth flow"""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured"
        )
    
    redirect_uri = f"{settings.APP_BASE_URL}/api/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_oauth_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {str(e)}"
        )
    
    access_token = token.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token received"
        )
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = await client.get("https://api.github.com/user", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from GitHub"
            )
        
        github_user = response.json()
    
    github_username = github_user.get("login")
    github_email = github_user.get("email")
    
    if not github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username not found"
        )
    
    user = db.query(User).filter(User.github_username == github_username).first()
    
    if user:
        user.email = github_email or user.email
        user.updated_at = datetime.utcnow()
    else:
        user = User(
            username=github_username,
            github_username=github_username,
            email=github_email,
            password_hash=None
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    session = create_session(db, user.id, github_token=access_token)
    
    return {
        "ok": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "github_username": user.github_username
        },
        "session_token": session.session_token,
        "expires_at": session.expires_at.isoformat()
    }


@router.post("/github/token")
async def github_token_login(
    data: GitHubTokenRequest,
    db: Session = Depends(get_db)
):
    """Login with GitHub Personal Access Token"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {data.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = await client.get("https://api.github.com/user", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid GitHub token"
            )
        
        github_user = response.json()
    
    github_username = github_user.get("login")
    github_email = github_user.get("email")
    
    if not github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username not found"
        )
    
    user = db.query(User).filter(User.github_username == github_username).first()
    
    if user:
        user.email = github_email or user.email
        user.updated_at = datetime.utcnow()
    else:
        user = User(
            username=github_username,
            github_username=github_username,
            email=github_email,
            password_hash=None
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    session = create_session(db, user.id, github_token=data.token)
    
    return {
        "ok": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "github_username": user.github_username
        },
        "session_token": session.session_token,
        "expires_at": session.expires_at.isoformat()
    }


@router.get("/github/repos")
async def get_github_repos(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's GitHub repositories"""
    session = db.query(AuthSession).filter(
        AuthSession.user_id == user.id,
        AuthSession.expires_at > datetime.utcnow()
    ).order_by(AuthSession.created_at.desc()).first()
    
    if not session or not session.github_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No GitHub token available. Please login via GitHub."
        )
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {session.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = await client.get(
            "https://api.github.com/user/repos?per_page=100&sort=updated",
            headers=headers
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch repositories from GitHub"
            )
        
        repos = response.json()
    
    return {
        "ok": True,
        "repos": [
            {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "private": repo["private"],
                "description": repo.get("description"),
                "html_url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "updated_at": repo["updated_at"],
                "language": repo.get("language"),
                "stargazers_count": repo["stargazers_count"],
                "forks_count": repo["forks_count"]
            }
            for repo in repos
        ]
    }
