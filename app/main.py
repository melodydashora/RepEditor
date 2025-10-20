"""
RepEditor FastAPI Backend
AI-Powered Repository Editor with GitHub integration
"""
import os
import time
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn

# --- Config imports (tolerant to missing attrs) ---
from app.core.config import settings, engine
from app.models.database import Base  # noqa: F401
from app.routes import chat, files, health, config, auth, repos, ai, ssh

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
STATIC_DIR = ROOT / "app" / "static"

def s(name: str, default=None):
    """Safe getattr on settings."""
    return getattr(settings, name, default)

def public_file(path: str) -> FileResponse:
    p = (PUBLIC_DIR / path).resolve()
    if not p.is_file():
        return JSONResponse({"ok": False, "error": f"Not found: {path}"}, status_code=404)
    # Infer content type for svg/js/html automatically via FileResponse
    return FileResponse(str(p))


# -------------------------------------------------------------------
# Lifespan (startup/shutdown)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 [RepEditor] Starting in {s('NODE_ENV','dev').upper()} mode")
    print(f"🚀 [RepEditor] Host: {s('HOST','0.0.0.0')}  Port: {s('PORT',5000)}")
    print(f"🚀 [RepEditor] UI Origin: {s('UI_ORIGIN','(not set)')}")
    # Triad names are optional; don’t blow up if unset
    print(f"🚀 [RepEditor] AI Models: {s('STRATEGIST_MODEL','gpt-5')} → {s('PLANNER_MODEL','gpt-5')} → {s('VALIDATOR_MODEL','gpt-5')}")

    # DB connectivity is optional; don’t crash on failure
    try:
        with engine.connect() as _:
            print("[db] ✅ PostgreSQL connection verified")
    except Exception as e:
        print(f"[db] ⚠️ Database connection check failed: {e}")

    yield

    print("[RepEditor] Shutting down gracefully…")
    try:
        engine.dispose()
    except Exception:
        pass


# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
app = FastAPI(
    title="RepEditor API",
    description="AI-Powered Repository Editor with GitHub integration and code assistance",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

# CORS — strict if UI_ORIGIN set, permissive in dev otherwise
allow_origins = [s("UI_ORIGIN")] if s("UI_ORIGIN") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# -------------------------------------------------------------------
# Static File Serving
# -------------------------------------------------------------------
# Explicit GET for extension.json (must be defined BEFORE mount)
@app.get("/public/extension.json")
async def serve_manifest():
    p = PUBLIC_DIR / "extension.json"
    return FileResponse(str(p), media_type="application/json")

# Serve repo-level public/ directory at /public
app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

# Return 499 on client disconnect (useful for SSE/long polls)
@app.middleware("http")
async def client_disconnect_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except asyncio.CancelledError:
        return PlainTextResponse("Client Disconnected", status_code=499)

# Timing header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    t0 = time.time()
    resp = await call_next(request)
    ms = (time.time() - t0) * 1000.0
    resp.headers["X-Process-Time-Ms"] = f"{ms:.2f}"
    return resp


# -------------------------------------------------------------------
# Error handlers
# -------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"ok": False, "error": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"ok": False, "error": "Validation error", "details": exc.errors()},
    )


# -------------------------------------------------------------------
# CORS Preflight Handler
# -------------------------------------------------------------------
@app.options("/{full_path:path}")
async def preflight_handler(request: Request):
    origin = request.headers.get("origin")
    if origin == getattr(settings, "UI_ORIGIN", None):
        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, PATCH, DELETE",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "600",
            },
        )
    return Response(status_code=status.HTTP_403_FORBIDDEN)


# -------------------------------------------------------------------
# Health endpoints (leave as-is)
# -------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "ok": True,
        "name": "Vecto Pilot API",
        "version": "4.1.0",
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env": s("NODE_ENV", "dev"),
    }

@app.get("/healthz")
async def kubernetes_health():
    return {"status": "ok", "ok": True, "healthy": True, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

@app.get("/ready")
async def kubernetes_readiness():
    return {"status": "ok", "ok": True, "ready": True, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

@app.get("/api/diagnostics")
async def diagnostics():
    return {
        "ok": True,
        "role": "gateway",
        "version": "5.0.0",
        "system": {
            "port": s("PORT", 5000),
            "host": s("HOST", "0.0.0.0"),
            "environment": s("NODE_ENV", "dev"),
            "is_production": s("is_production", False),
            "is_replit": s("is_replit", False),
        },
        "ports": {
            "gateway": {"port": s("PORT", 5000), "host": s("HOST", "0.0.0.0"), "public": True},
            "sdk": {"port": 3101, "host": "127.0.0.1", "public": False, "note": "Internal only - handles AI assistant"},
            "agent": {"port": 3102, "host": "127.0.0.1", "public": False, "note": "Internal only - workspace intelligence"},
        },
        "topology": {
            "gateway_host": s("HOST", "0.0.0.0"),
            "sdk_host": "127.0.0.1",
            "agent_host": "127.0.0.1",
            "external_only_gateway": True,
            "note": "Only Gateway (port 5000) should be externally reachable",
        },
        "ai_models": {
            "assistant": {"model": "gpt-5", "provider": "openai", "endpoint": "/api/chat"},
            "triad": {
                "strategist": s("STRATEGIST_MODEL", "gpt-5"),
                "planner": s("PLANNER_MODEL", "gpt-5"),
                "validator": s("VALIDATOR_MODEL", "gpt-5"),
            },
        },
        "integrations": {
            "anthropic": bool(s("ANTHROPIC_API_KEY")),
            "openai": bool(s("OPENAI_API_KEY")),
            "google_maps": bool(s("GOOGLE_MAPS_API_KEY")),
            "google_ai": bool(s("GOOGLEAQ_API_KEY")),
            "perplexity": bool(s("PERPLEXITY_API_KEY")),
            "faa": bool(s("FAA_ASWS_CLIENT_ID")),
        },
        "database": {"connected": bool(s("DATABASE_URL"))},
    }


# -------------------------------------------------------------------
# Assistant override probe (used by the extension/UI)
# -------------------------------------------------------------------
from typing import Optional
from fastapi import Header

@app.api_route("/api/assistant/verify-override", methods=["GET", "POST", "OPTIONS"])
async def verify_assistant_override(
    t: Optional[int] = None,                               # optional cache-buster query
    authorization: Optional[str] = Header(default=None),   # optional Bearer token
):
    # Optional token check (enable if you want to require the override token)
    # Expected: Authorization: Bearer <ASSISTANT_OVERRIDE_TOKEN>
    override_token = s("ASSISTANT_OVERRIDE_TOKEN")
    if override_token:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"ok": False, "error": "Missing or invalid Authorization header"}
            )
        supplied = authorization.split(" ", 1)[1].strip()
        if supplied != override_token:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"ok": False, "error": "Invalid override token"}
            )

    # If we got here, override is permitted
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "ok": True,
            "override": True,
            "mode": "assistant-override",
            "ts": int(time.time() * 1000),
        },
    )


# -------------------------------------------------------------------
# Static pages required by the Extension
# -------------------------------------------------------------------
@app.get("/")
def root(): return public_file("chat.html")
@app.get("/chat")
def chat_page(): return public_file("chat.html")

@app.get("/extension.json")
def extension_manifest(): return public_file("extension.json")

@app.get("/gpt-frame.html")
def extension_gpt_frame(): return public_file("gpt-frame.html")

@app.get("/panel.html")
def extension_panel(): return public_file("panel.html")

@app.get("/panel.js")
def extension_panel_js(): return public_file("panel.js")

@app.get("/icon.svg")
def extension_icon(): return public_file("icon.svg")

@app.get("/diff.html")
def extension_diff(): return public_file("diff.html")

@app.get("/diff.js")
def extension_diff_js(): return public_file("diff.js")

@app.get("/logs.html")
def extension_logs(): return public_file("logs.html")

@app.get("/logs.js")
def extension_logs_js(): return public_file("logs.js")

@app.get("/background.html")
def extension_background(): return public_file("background.html")

@app.get("/sql.html")
def extension_sql(): return public_file("sql.html")

@app.get("/svg-editor.html")
def extension_svg_editor(): return public_file("svg-editor.html")

@app.get("/config.html")
def extension_config(): return public_file("config.html")

# Optional icons (serve if present; otherwise 404 handled above)
@app.get("/sql-icon.svg")
def extension_sql_icon(): return public_file("sql-icon.svg")

@app.get("/vecto-icon.svg")
def extension_vecto_icon(): return public_file("vecto-icon.svg")

# Back-compat static path
@app.get("/app/static/vecto-icon.svg")
def extension_vecto_icon_static(): return public_file("vecto-icon.svg")


# -------------------------------------------------------------------
# Mount static dirs (safe if missing)
# -------------------------------------------------------------------
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=False), name="static")


# -------------------------------------------------------------------
# API Routers
# -------------------------------------------------------------------
# If any include fails (missing module), don’t crash the whole app.
for r in (
    ("auth", auth.router),
    ("repos", repos.router),
    ("ai", ai.router),
    ("ssh", ssh.router),
    ("chat", chat.router),
    ("chat.providers_router", getattr(chat, "providers_router", None)),
    ("files", files.router),
    ("config", config.router),
    ("health", health.router),
):
    name, router = r
    if router is not None:
        try:
            app.include_router(router)
        except Exception as e:
            print(f"[routes] ⚠️ Skipped router {name}: {e}")


# -------------------------------------------------------------------
# Entry
# -------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=s("HOST", "0.0.0.0"),
        port=int(s("PORT", 5000)),
        reload=not bool(s("is_production", False)),
        log_level="info",
        access_log=True,
    )
