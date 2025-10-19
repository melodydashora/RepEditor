"""
RepEditor FastAPI Backend
AI-Powered Repository Editor with GitHub integration
"""
import os
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from app.core.config import settings, engine
from app.models.database import Base
from app.routes import chat, files, health, config, auth, repos, ai, ssh


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    # Startup
    print(f"🚀 [RepEditor] Starting in {settings.NODE_ENV.upper()} mode")
    print(f"🚀 [RepEditor] Port: {settings.PORT}, Host: {settings.HOST}")
    print(f"🚀 [RepEditor] UI Origin: {settings.UI_ORIGIN}")
    print(f"🚀 [RepEditor] AI Models: {settings.STRATEGIST_MODEL} → {settings.PLANNER_MODEL} → {settings.VALIDATOR_MODEL}")
    
    # Verify database connection
    try:
        with engine.connect() as conn:
            print("[db] ✅ PostgreSQL connection verified")
    except Exception as e:
        print(f"[db] ⚠️  Database connection failed: {e}")
    
    yield
    
    # Shutdown
    print("[RepEditor] Shutting down gracefully...")
    engine.dispose()


# Initialize FastAPI app
app = FastAPI(
    title="RepEditor API",
    description="AI-Powered Repository Editor with GitHub integration and code assistance",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# PRODUCTION-GRADE MIDDLEWARE (per attached requirements)
# ============================================================================

# Trust proxy configuration (Replit platform has exactly 1 proxy layer)
app.state.trust_proxy = 1


# CORS: strict origin validation for vectopilot.com only
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """Manual CORS with strict origin validation and Vary header"""
    origin = request.headers.get("origin")
    response = await call_next(request)
    
    # Set Vary header to prevent cache poisoning
    response.headers["Vary"] = "Origin"
    
    # Allow no-origin requests (curl, server-to-server)
    if not origin:
        return response
    
    # Strict origin check: only vectopilot.com
    if origin == settings.UI_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    else:
        # Reject unauthorized origins
        pass
    
    return response


# Handle preflight OPTIONS requests
@app.options("/{full_path:path}")
async def preflight_handler(request: Request):
    """Handle CORS preflight requests"""
    origin = request.headers.get("origin")
    
    if origin == settings.UI_ORIGIN:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "600",
            }
        )
    
    return Response(status_code=status.HTTP_403_FORBIDDEN)


# Client abort detection (return 499 without noise)
@app.middleware("http")
async def client_disconnect_handler(request: Request, call_next):
    """Handle client disconnects gracefully (499 status)"""
    try:
        response = await call_next(request)
        return response
    except asyncio.CancelledError:
        # Client disconnected mid-request (common in SSE)
        return PlainTextResponse("Client Disconnected", status_code=499)


# Request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    return response


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "ok": False}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "details": exc.errors(), "ok": False}
    )


# ============================================================================
# HEALTH & DIAGNOSTIC ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "ok": True,
        "name": "Vecto Pilot API",
        "version": "4.1.0",
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env": settings.NODE_ENV
    }


@app.get("/healthz")
async def kubernetes_health():
    """Kubernetes-style health check"""
    return {
        "status": "ok",
        "ok": True,
        "healthy": True,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


@app.get("/ready")
async def kubernetes_readiness():
    """Kubernetes-style readiness check"""
    return {
        "status": "ok",
        "ok": True,
        "ready": True,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


@app.get("/api/diagnostics")
async def diagnostics():
    """System diagnostics endpoint with topology validation"""
    return {
        "ok": True,
        "role": "gateway",
        "version": "5.0.0",
        "system": {
            "port": settings.PORT,
            "host": settings.HOST,
            "environment": settings.NODE_ENV,
            "is_production": settings.is_production,
            "is_replit": settings.is_replit,
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
        "topology": {
            "gateway_host": settings.HOST,
            "sdk_host": "127.0.0.1",
            "agent_host": "127.0.0.1",
            "external_only_gateway": True,
            "note": "Only Gateway (port 5000) should be externally reachable"
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
                "validator": settings.VALIDATOR_MODEL,
            }
        },
        "integrations": {
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "openai": bool(settings.OPENAI_API_KEY),
            "google_maps": bool(settings.GOOGLE_MAPS_API_KEY),
            "google_ai": bool(settings.GOOGLEAQ_API_KEY),
            "perplexity": bool(settings.PERPLEXITY_API_KEY),
            "faa": bool(settings.FAA_ASWS_CLIENT_ID),
        },
        "database": {
            "connected": True if settings.DATABASE_URL else False,
        }
    }


@app.get("/")
async def root():
    """Landing page - AI Chat Assistant"""
    from fastapi.responses import FileResponse
    return FileResponse("public/chat.html")


@app.get("/chat")
async def chat_page():
    """AI Chat Assistant page"""
    from fastapi.responses import FileResponse
    return FileResponse("public/chat.html")


@app.get("/extension.json")
async def extension_manifest():
    """Replit Extension manifest for workspace tool"""
    from fastapi.responses import FileResponse
    # Serve the correct extension.json from public directory
    return FileResponse("public/extension.json")


@app.get("/gpt-frame.html")
async def extension_gpt_frame():
    """Extension AI Assistant HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/gpt-frame.html")


@app.get("/panel.html")
async def extension_panel():
    """Extension Repo Fixer panel HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/panel.html")


@app.get("/panel.js")
async def extension_panel_js():
    """Extension panel JavaScript"""
    from fastapi.responses import FileResponse
    return FileResponse("public/panel.js")


@app.get("/icon.svg")
async def extension_icon():
    """Extension icon"""
    from fastapi.responses import FileResponse
    return FileResponse("public/icon.svg")


@app.get("/diff.html")
async def extension_diff():
    """Extension diff viewer HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/diff.html")


@app.get("/diff.js")
async def extension_diff_js():
    """Extension diff viewer JavaScript"""
    from fastapi.responses import FileResponse
    return FileResponse("public/diff.js")


@app.get("/logs.html")
async def extension_logs():
    """Extension logs viewer HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/logs.html")


@app.get("/logs.js")
async def extension_logs_js():
    """Extension logs viewer JavaScript"""
    from fastapi.responses import FileResponse
    return FileResponse("public/logs.js")


@app.get("/background.html")
async def extension_background():
    """Extension background service HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/background.html")


@app.get("/sql.html")
async def extension_sql():
    """Extension SQL viewer HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/sql.html")


@app.get("/sql-icon.svg")
async def extension_sql_icon():
    """SQL viewer icon"""
    from fastapi.responses import FileResponse
    return FileResponse("public/sql-icon.svg", media_type="image/svg+xml")


@app.get("/vecto-icon.svg")
async def extension_vecto_icon():
    """Vecto Pilot icon"""
    from fastapi.responses import FileResponse
    return FileResponse("public/vecto-icon.svg", media_type="image/svg+xml")


# Route for backward compatibility - remove after transition
@app.get("/app/static/vecto-icon.svg")
async def extension_vecto_icon_static():
    """Vecto Pilot icon (static path)"""
    from fastapi.responses import FileResponse
    return FileResponse("public/vecto-icon.svg", media_type="image/svg+xml")


@app.get("/svg-editor.html")
async def extension_svg_editor():
    """Extension SVG editor HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/svg-editor.html")


@app.get("/config.html")
async def extension_config():
    """Extension settings HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("public/config.html")


# ============================================================================
# API ROUTES
# ============================================================================

# Mount static files
from fastapi.staticfiles import StaticFiles
# Mount static files from app/static directory  
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register API routers
app.include_router(auth.router)  # Authentication (GitHub OAuth + username/password)
app.include_router(repos.router)  # Repository cloning and git operations
app.include_router(ai.router)  # AI autofix system (GPT-5 + Codex)
app.include_router(ssh.router)  # SSH access to Replit apps
app.include_router(chat.router)  # AI chat interface
app.include_router(chat.providers_router)  # AI provider models endpoint
app.include_router(files.router)  # File operations
app.include_router(config.router)  # Configuration
app.include_router(health.router)  # Health check


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production,
        log_level="info",
        access_log=True,
    )
