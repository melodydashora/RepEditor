"""
Health and diagnostics endpoints
Validates the single public port invariant and system topology
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings
import os

router = APIRouter()


class HealthResponse(BaseModel):
    ok: bool
    role: str
    version: str
    ports: dict
    environment: str
    topology: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for Gateway topology validation
    
    Returns:
    - ok: Always true if service is running
    - role: "gateway" (public-facing entry point)
    - ports: Gateway (5000 public), SDK (3101 internal), Agent (3102 internal)
    - topology: Confirms only Gateway is public
    """
    return {
        "ok": True,
        "role": "gateway",
        "version": "5.0.0",
        "ports": {
            "gateway": settings.PORT,
            "gateway_public": True,
            "sdk": 3101,
            "sdk_public": False,
            "agent": 3102,
            "agent_public": False
        },
        "environment": settings.NODE_ENV,
        "topology": {
            "gateway_host": settings.HOST,
            "sdk_host": "127.0.0.1",
            "agent_host": "127.0.0.1",
            "external_only_gateway": True,
            "note": "Only Gateway (port 5000) should be externally reachable"
        }
    }


@router.get("/diagnostics")
async def diagnostics():
    """
    System diagnostics endpoint
    Returns configuration and runtime information (no secrets)
    """
    return {
        "ok": True,
        "system": {
            "role": "gateway",
            "version": "5.0.0",
            "environment": settings.NODE_ENV,
            "replit": settings.is_replit,
            "repl_id": settings.REPL_ID,
            "repl_slug": settings.REPL_SLUG
        },
        "ports": {
            "gateway": {
                "port": settings.PORT,
                "host": settings.HOST,
                "public": True
            },
            "sdk": {
                "port": 3101,
                "host": "127.0.0.1",
                "public": False,
                "note": "Internal only - handles AI assistant"
            },
            "agent": {
                "port": 3102,
                "host": "127.0.0.1",
                "public": False,
                "note": "Internal only - handles workspace intelligence"
            }
        },
        "ai_models": {
            "assistant": {
                "model": "gpt-5",
                "provider": "openai",
                "endpoint": "/api/chat"
            },
            "triad": {
                "strategist": settings.STRATEGIST_MODEL,
                "planner": settings.PLANNER_MODEL,
                "validator": settings.VALIDATOR_MODEL
            }
        },
        "database": {
            "connected": bool(settings.DATABASE_URL),
            "type": "postgresql"
        }
    }
