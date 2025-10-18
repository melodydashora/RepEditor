"""AI Chat Assistant API routes with full repo access"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
import subprocess
from pathlib import Path

from openai import AsyncOpenAI
from app.core.config import settings


router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat message request"""
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []


class ChatResponse(BaseModel):
    """Chat message response"""
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = []


# Tool functions for GPT-5
def read_file(file_path: str) -> str:
    """Read a file from the repository"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return f"File: {file_path}\n\n{content}"
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return f"✅ Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing {file_path}: {str(e)}"


def list_directory(directory: str = ".") -> str:
    """List files in a directory"""
    try:
        result = subprocess.run(
            ["ls", "-la", directory],
            capture_output=True,
            text=True,
            timeout=5
        )
        return f"Directory: {directory}\n\n{result.stdout}"
    except Exception as e:
        return f"Error listing {directory}: {str(e)}"


def search_files(pattern: str, directory: str = ".") -> str:
    """Search for files matching a pattern"""
    try:
        result = subprocess.run(
            ["find", directory, "-name", pattern, "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return f"Files matching '{pattern}':\n\n{result.stdout}"
    except Exception as e:
        return f"Error searching: {str(e)}"


def grep_code(pattern: str, directory: str = "app") -> str:
    """Search for text/code patterns in files"""
    try:
        result = subprocess.run(
            ["grep", "-r", "-n", "-i", pattern, directory],
            capture_output=True,
            text=True,
            timeout=10
        )
        return f"Matches for '{pattern}':\n\n{result.stdout if result.stdout else 'No matches found'}"
    except Exception as e:
        return f"Error searching code: {str(e)}"


def execute_command(command: str) -> str:
    """Execute a safe shell command"""
    # Whitelist safe commands
    allowed_commands = ["ls", "find", "grep", "cat", "head", "tail", "wc", "tree", "pwd", "python", "pip"]
    
    cmd_parts = command.split()
    if not cmd_parts or cmd_parts[0] not in allowed_commands:
        return f"❌ Command '{cmd_parts[0] if cmd_parts else command}' not allowed. Safe commands: {', '.join(allowed_commands)}"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Command: {command}\n\n{output}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def get_repo_structure() -> str:
    """Get the repository structure"""
    try:
        result = subprocess.run(
            ["find", ".", "-type", "f", "-name", "*.py", "-o", "-name", "*.ts", "-o", "-name", "*.js"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return f"Repository code files:\n\n{result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"


# Tool definitions for GPT-5
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read (e.g., 'app/main.py', 'server/eidolon/index.ts')"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or update a file in the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to list (default: current directory)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Find files by name pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "File name pattern (e.g., '*.py', 'config*')"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_code",
            "description": "Search for text patterns in code files",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text pattern to search for"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in (default: app)"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a safe shell command (ls, grep, cat, head, tail, wc, tree, pwd, python, pip)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_repo_structure",
            "description": "Get overview of repository structure (all code files)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# Map function names to actual functions
FUNCTION_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "search_files": search_files,
    "grep_code": grep_code,
    "execute_command": execute_command,
    "get_repo_structure": get_repo_structure
}


@router.post("", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with AI assistant with FULL repository access
    
    GPT-5 can:
    - Read any file in the repo
    - Write/edit files
    - Search code and files
    - Execute safe shell commands
    - List directories
    - Analyze and refactor code
    """
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = """VECTO PILOT ASSISTANT - Complete Repository Knowledge

=== TOOLS ===
read_file, write_file, search_files, grep_code, list_directory, execute_command, get_repo_structure

=== REPOSITORY STRUCTURE ===

app/ (Python FastAPI - NEW PRIMARY SYSTEM):
├── main.py - FastAPI app, port 5000, serves chat.html at root, mounts static files
├── core/
│   ├── config.py - Settings, DATABASE_URL, OPENAI_API_KEY, environment config
├── mlops/
│   ├── triad_orchestrator.py - Triad pipeline: Claude → GPT-5 → Gemini
│   ├── event_store.py - SQLite event logging for ML training
│   ├── observability.py - Metrics, drift detection, monitoring
│   ├── safety_guardrails.py - RELEASE_TOKEN, canary rollouts
│   ├── adapters/
│   │   ├── factory.py - Model adapter factory pattern
│   │   ├── openai_adapter.py - GPT-5 adapter
│   │   ├── anthropic_adapter.py - Claude adapter
│   │   ├── google_adapter.py - Gemini adapter
│   ├── pipelines/
│       ├── training.py - ML training pipeline
│       ├── evaluation.py - Model evaluation
│       ├── finetuning.py - Fine-tuning infrastructure
├── models/
│   ├── database.py - 15 PostgreSQL tables for ML tracking
├── routes/
│   ├── chat.py - This file! GPT-5 chat with function calling
│   ├── files.py - File tree API endpoint
│   ├── strategy.py - /api/strategy/generate (Triad), performance metrics
│   ├── mlops.py - 20+ MLOps admin endpoints (training, eval, deploy)
├── static/
    ├── chat.html - Interactive chat UI with file tree sidebar

server/ (Legacy Node.js - Being Phased Out):
├── gateway-server.js - Port 5000 proxy, Vite still wired (needs removal)
├── agent-server.js - Port 43717→3102 target
├── eidolon/
│   ├── index.ts - Main export: buildCodeMap, readJson/writeJson, contextAwareness, memoryManager
│   ├── config.ts - Eidolon configuration
│   ├── core/
│   │   ├── code-map.ts - Workspace code mapping
│   │   ├── context-awareness.ts - Deep context tracking
│   │   ├── memory-enhanced.ts - Enhanced memory system
│   │   ├── memory-store.ts - writeJson/readJson versioned storage (data/memory/)
│   │   ├── deep-thinking-engine.ts - Advanced reasoning
│   │   ├── deployment-tracker.ts - Deployment tracking
│   │   ├── llm.ts - LLM interface
│   ├── memory/
│   │   ├── pg.js - PostgreSQL memory backend
│   │   ├── compactor.js - Memory compaction
│   ├── tools/
│       ├── mcp-diagnostics.js - MCP diagnostics
│       ├── sql-client.ts - SQL execution
├── lib/
│   ├── triad-orchestrator.js - Legacy Triad (migrated to Python)
│   ├── gpt5-tactical-planner.js - GPT-5 venue generation
│   ├── strategy-generator.js - Claude strategy generation
│   ├── validator-gemini.js - Gemini validation
│   ├── scoring-engine.js - Venue ranking/scoring
│   ├── geocoding.js - Google Geocoding API
│   ├── routes-api.js - Google Routes API
│   ├── perplexity-research.js - Perplexity sonar-pro
│   ├── adapters/
│       ├── anthropic-sonnet45.js - Claude Sonnet 4.5
│       ├── openai-gpt5.js - GPT-5
│       ├── gemini-2.5-pro.js - Gemini 2.5 Pro
├── routes/
│   ├── blocks.js - Main recommendation endpoint
│   ├── blocks-triad-strict.js - Triad-based blocks
│   ├── location.js - Location/snapshot handling
│   ├── diagnostics.js - System diagnostics
│   ├── health.js - Health check
│   ├── feedback.js - User feedback collection
├── db/
│   ├── 001_init.sql - Database schema
│   ├── 002_seed_dfw.sql - Frisco, TX venue catalog (143 venues)
│   ├── migrations/ - Database migrations
├── data/
    ├── blocks.dfw.json - DFW venue data
    ├── policy.default.json - Default policy config

=== THREE-PHASE ARCHITECTURE ===

Phase A - Client Location Flow (GPS → Snapshot → Context):
- GPS via Browser Geolocation API → useGeoPosition → LocationContext
- Snapshot creation with source tracking (GPS/override/search)
- Session ID increments on GPS refresh or city search
- AbortController prevents stale enrichment
- Files: client/src/components/location-context-clean.tsx, useGeoPosition.ts

Phase B - Server Blocks/Strategy (Snapshot → AI → Venues):
- Triad Pipeline: Claude Strategist → GPT-5 Planner → Gemini Validator
- Claude: Strategic analysis, pro tips, earnings estimates
- GPT-5: Venue generation (4-6 specific venues), tactical planning
- Gemini: JSON validation, minimum recommendation enforcement
- Range policy: 0-15min base, 20-30min expand
- Scoring: Proximity + reliability + event intensity + personalization
- Files: server/lib/triad-orchestrator.js, scoring-engine.js, gpt5-tactical-planner.js

Phase C - Eidolon Override (Assistant Interception):
- Gateway intercepts /assistant/* requests
- Enhanced memory via data/memory/ JSON versioned storage
- Cross-session awareness, persistent identity
- Files: server/eidolon/index.ts, core/memory-enhanced.ts, core/context-awareness.ts

=== CURRENT SYSTEM STATE ===

Python FastAPI (Active):
- Port 5000 public API
- /api/strategy/generate - Triad pipeline endpoint
- /api/chat - This chat assistant (GPT-5 with tools)
- /api/files/tree - Repository file tree
- /api/mlops/* - 20+ MLOps endpoints
- PostgreSQL: 15 ML tables, event store
- Running: uvicorn app.main:app --host 0.0.0.0 --port 5000

Node.js Legacy (Phasing Out):
- Gateway on port 5000 (Vite still wired - needs removal)
- SDK on 127.0.0.1:3101 (internal)
- Agent on 43717 (target: 3102)
- Needs: CORS gate for UI_ORIGIN, remove Vite, port change

=== KEY DESIGN PATTERNS ===

Triad Invariants:
- Single-path only (no fallbacks) - fail-fast on errors
- Claude → GPT-5 → Gemini (strict order)
- Each stage has specific role, no mixing

Memory System:
- writeJson(root, name, data) - Versioned writes to data/memory/
- readJson(root, name) - Read from .latest.json or fallback
- Timestamps: ISO format, file versioning
- Format: {version, createdAt, data}

Global Support:
- Works worldwide via GPS (not just Frisco catalog)
- GPT-5 generates venues from coordinates when catalog empty
- H3 geospatial: Pre-filter haversine (100km) before gridDistance
- Null city → formatted address or coordinates

ML Training:
- Event store: SQLite logging all model interactions
- PostgreSQL: 15 tables (rankings, candidates, feedback, sessions, etc.)
- Counterfactual learning ready
- Per-ranking feedback system

=== GATEWAY-CORE CUTOVER TODO ===
1. Remove Vite middleware + SPA from gateway-server.js
2. Add CORS gate for UI_ORIGIN (https://vectopilot.com)
3. Change Agent port to 3102
4. Keep SDK watchdog & proxies (/api/*, /eidolon/*, /assistant/*)
5. Complete migration to Python FastAPI

=== OPERATING RULES ===
- Use tools immediately when needed. No overthinking.
- Read files before editing them.
- Execute commands directly (allowed: ls, grep, cat, head, tail, wc, tree, pwd, python, pip).
- Be concise. Show results, not process.
- Format code with ```language blocks.
- Identify which phase (A/B/C) a question relates to.
- Reference actual file paths from the structure above.

You are an autonomous coding agent with complete repository knowledge. Act directly."""

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(request.conversation_history)
        messages.append({"role": "user", "content": request.message})
        
        # Initial GPT-5 call with tools
        response = await client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_completion_tokens=4000
        )
        
        response_message = response.choices[0].message
        tool_calls_made = []
        
        # Execute tool calls if any
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the function
                if function_name in FUNCTION_MAP:
                    function_result = FUNCTION_MAP[function_name](**function_args)
                    tool_calls_made.append({
                        "function": function_name,
                        "args": function_args,
                        "result": function_result[:500]  # Truncate for response
                    })
                    
                    # Add function result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_result
                    })
            
            # Get final response after tool execution
            final_response = await client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                max_completion_tokens=4000
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = response_message.content
        
        return ChatResponse(
            response=final_content,
            tool_calls=tool_calls_made if tool_calls_made else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
