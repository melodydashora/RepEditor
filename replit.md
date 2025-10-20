# RepEditor - AI-Powered Repository Editor

## Overview
RepEditor is a production-ready Replit Extension providing AI-powered repository editing capabilities:
- Full repository access and code editing with GPT-5, Claude, and Gemini models
- GitHub OAuth authentication and repository management
- Real-time chat interface with streaming responses
- Support for both function-calling and specialized models
- 5 workspace tools and 3 file handlers for comprehensive development support

## Extension Status ✅ READY TO PUBLISH

### Extension Manifest
- **Fixed**: Updated to Replit-compliant schema format using `handler`, `glob`, `scopes: [{name, reason}]`, `background: {page}`
- **Working**: All 5 tools loading: AI Assistant, Repo Fixer, SQL Viewer, Logs & Diagnostics, Settings
- **Working**: All 3 file handlers: SVG Editor (.svg), Diff Viewer (.diff), Patch Viewer (.patch)
- **Working**: Background page support at `/background.html`

### API Endpoints - ALL FIXED ✅
- **Fixed**: `/api/assistant/verify-override` endpoint now returns 200 OK (was 405 Method Not Allowed)
- **Working**: CORS preflight handler returns proper Response objects
- **Working**: Extension manifest served at `/public/extension.json`
- **Working**: All HTML files served at root paths (e.g., `/gpt-frame.html`, `/panel.html`)

## Publishing Instructions

1. **Clear Extension Cache**
   - Extensions → DevTools → 3-dot menu → Clear Local Extension Cache

2. **Load Extension**
   - Click "Load Locally"
   - Should see: "Adding extension: GPT Repository Access" (not "Unnamed Extension")

3. **Create Release**
   - Configure tab settings:
     - Build command: `npm run build` (or leave blank)
     - Output folder: `public`
   - Add listing details:
     - Title: GPT Repository Access
     - Icon: `/icon.svg`
     - Tags: AI, Git, Repository, Assistant
     - Background page: `/background.html`
   - Click **Publish** (Public)

## Project Architecture

### Authentication System
- **Dual Authentication**: GitHub OAuth + username/password login
- **Session Management**: 30-day session tokens with Bearer authentication
- **Repository Access**: GitHub token storage for cloning private repos
- **Database**: PostgreSQL with SQLAlchemy ORM

### AI Provider Support
- **OpenAI**: GPT-4, GPT-5, Codex models
- **Anthropic**: Claude Sonnet 4.5, Claude Opus
- **Google**: Gemini 2.5 Pro, Gemini Flash

### Repository Management
- Clone GitHub repositories to local workspace
- Browse file trees
- Read file contents
- Git operations (commit, push)
- Secure path validation

### Tech Stack
- **Backend**: FastAPI, Python 3.11, Uvicorn
- **Database**: PostgreSQL with asyncpg
- **Auth**: Authlib, passlib, python-jose, bcrypt
- **AI SDKs**: OpenAI, Anthropic, Google Generative AI
- **Frontend**: HTML, CSS, JavaScript (vanilla)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Username/password registration
- `POST /api/auth/login` - Username/password login
- `GET /api/auth/github/start` - GitHub OAuth initiation
- `GET /api/auth/github/callback` - GitHub OAuth callback
- `POST /api/auth/github/token` - Manual GitHub PAT login
- `GET /api/auth/github/repos` - List user's GitHub repositories
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Invalidate session

### Repository Management
- `POST /api/repos/select` - Clone/select repository
- `GET /api/repos/tree` - Get file tree
- `GET /api/repos/file` - Read file content
- `POST /api/repos/git/config` - Configure git user
- `POST /api/repos/git/commit` - Commit changes
- `POST /api/repos/git/push` - Push to remote
- `GET /api/repos/git/status` - Get git status

### AI Chat
- `POST /api/chat` - Send message to AI assistant
- `GET /api/chat/providers` - List available AI providers/models
- `GET /api/chat/history` - Get conversation history
- `GET /api/assistant/verify-override` - Verify assistant override token ✅ FIXED

### AI Autofix System (6 endpoints)
- `/api/ai/plan` - GPT-5 analyzes repo and creates fix plan
- `/api/ai/diff` - Codex generates unified diff patches  
- `/api/ai/apply` - Auto-commits, pushes branch, and opens PR
- `/api/ai/autofix` - One-click: plan → diff → apply → PR
- `/api/ai/tree` - Browse GitHub repo file tree
- `/api/ai/file` - Read file contents from GitHub repos

### SSH Access System (7 endpoints)
- `/api/ssh/keygen` - Generate SSH keypairs for Replit authentication
- `/api/ssh/keys` - List stored SSH keys
- `/api/ssh/connect` - Get SSH connection details for any Repl
- `/api/ssh/exec` - Execute commands on remote Repls
- `/api/ssh/repls` - List available Replit apps
- `/api/ssh/browse` - Browse files in remote Repls
- `/api/ssh/read` - Read file contents from remote Repls

## Environment Variables
Required secrets:
- `DATABASE_URL` - PostgreSQL connection string
- `GITHUB_CLIENT_ID` - GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET` - GitHub OAuth app secret
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLEAQ_API_KEY` - Google AI API key
- `APP_BASE_URL` - Application base URL for OAuth callbacks
- `ASSISTANT_OVERRIDE_TOKEN` - Optional token for assistant override

## Recent Updates

### October 20, 2025 - EXTENSION FULLY FUNCTIONAL ✅
- **Fixed ALL Critical Issues**:
  - ✅ Updated extension.json to proper Replit schema format
  - ✅ Added missing `/api/assistant/verify-override` endpoint (was causing 405 errors)
  - ✅ CORS preflight handler returns proper Response objects
  - ✅ All HTML files served at root paths
  - ✅ Extension manifest properly served at /public/extension.json
- **Extension Ready**: All 5 tools + 3 file handlers + background page working
- **Publishable**: Ready for Replit Extension Store

### Previous Updates
- **Extension Schema Migration**: Updated to proper Replit extension format
- **AI Autofix System**: 6 endpoints for GPT-5 planning + Codex diff generation
- **SSH Access System**: 7 endpoints for direct Replit app remote access
- **GPT Frame Integration**: Added proper Replit Extension with workspace panel
- **GitHub Authentication**: OAuth + manual token support
- **Repository Management**: Clone, browse, commit, push capabilities

## Repository
- **GitHub**: git@github.com:melodydashora/RepEditor.git
- **Project Name**: RepEditor (AI-Powered Repository Editor)
- **Status**: Production-Ready Extension

## User Investment
- **Financial**: $400+ invested
- **Time**: 18+ hours of development
- **Expectation**: Fully functional, professional-grade extension