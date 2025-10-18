# RepEditor - Complete Feature List

## 🎯 Core Features

### 1. AI-Powered Repository Editor
- **Multi-Provider Support**: OpenAI (GPT-4, GPT-5, Codex), Anthropic (Claude), Google (Gemini)
- **Full Repository Access**: Read, write, search, and analyze any file
- **Real-time Chat Interface**: Streaming responses with function calling
- **GitHub Integration**: OAuth + PAT authentication, clone repos, manage access

### 2. Authentication System
- **Dual Auth**: GitHub OAuth + username/password
- **Session Management**: 30-day tokens with Bearer auth
- **Repository Access**: Secure GitHub token storage for private repos
- **Database**: PostgreSQL with SQLAlchemy ORM

### 3. AI Autofix System (6 Endpoints)
- `/api/ai/plan` - GPT-5 analyzes repo and creates fix plan
- `/api/ai/diff` - Codex generates unified diff patches
- `/api/ai/apply` - Auto-commit, push branch, open PR
- `/api/ai/autofix` - One-click: plan → diff → apply → PR
- `/api/ai/tree` - Browse GitHub repo file tree
- `/api/ai/file` - Read file contents from GitHub

### 4. SSH Access System (7 Endpoints)
- `/api/ssh/keygen` - Generate SSH keypairs
- `/api/ssh/keys` - List stored keys
- `/api/ssh/connect` - Get SSH connection details
- `/api/ssh/exec` - Execute commands on remote Repls
- `/api/ssh/repls` - List available Replit apps
- `/api/ssh/browse` - Browse files in remote Repls
- `/api/ssh/read` - Read file contents from remote Repls

### 5. Replit Extension (Workspace Panel)
- **Two Panels**: Main AI panel + Diff viewer
- **Full Permissions**: Read, write, execute, ReplDB, experimental APIs, network
- **FS Bridge**: Direct filesystem access to current workspace
- **Universal**: Works in ANY Repl with `.replit` config

---

## 🤖 GPT-5 Tool Arsenal (18 Tools)

### File System (6 tools)
1. `read_file` - Read any file from repository
2. `write_file` - Write/edit files with full content
3. `list_directory` - Browse directory contents
4. `search_files` - Find files by name pattern
5. `grep_code` - Search code content with regex
6. `get_repo_structure` - Full repository tree view

### Git Operations (4 tools)
7. `git_status` - Check working tree status
8. `git_diff` - View uncommitted changes
9. `git_commit` - Commit changes with message
10. `git_push` - Push to remote repository

### Database (3 tools)
11. `sql_query` - Execute SELECT queries (PostgreSQL)
12. `sql_execute` - Execute INSERT/UPDATE/DELETE
13. `get_database_schema` - Inspect tables and columns

### System & Intelligence (5 tools)
14. `execute_command` - Run shell commands safely
15. `analyze_workspace` - Project structure analysis
16. `web_search` - Real-time web search (Perplexity)
17. `get_memory` - Read persistent JSON storage
18. `write_memory` - Write versioned memory storage

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Username/password login
- `GET /api/auth/github/start` - GitHub OAuth start
- `GET /api/auth/github/callback` - GitHub OAuth callback
- `POST /api/auth/github/token` - Manual GitHub PAT
- `GET /api/auth/github/repos` - List user's repos
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - Invalidate session

### Repository Management
- `POST /api/repos/select` - Clone/select repo
- `GET /api/repos/tree` - File tree
- `GET /api/repos/file` - Read file content
- `POST /api/repos/git/config` - Configure git
- `POST /api/repos/git/commit` - Commit changes
- `POST /api/repos/git/push` - Push to remote
- `GET /api/repos/git/status` - Git status

### AI Chat
- `POST /api/chat` - Chat with AI (streaming)
- `GET /api/chat/providers` - List AI providers/models
- `GET /api/chat/history` - Conversation history
- `GET /api/chat/frame` - Embedded GPT frame

### AI Autofix
- `POST /api/ai/plan` - Analyze & create fix plan
- `POST /api/ai/diff` - Generate code diffs
- `POST /api/ai/apply` - Auto-commit & PR
- `POST /api/ai/autofix` - All-in-one autofix
- `GET /api/ai/tree` - Browse GitHub repo tree
- `GET /api/ai/file` - Read GitHub file

### SSH Access
- `POST /api/ssh/keygen` - Generate SSH keys
- `GET /api/ssh/keys` - List SSH keys
- `POST /api/ssh/connect` - Connect to Repl
- `POST /api/ssh/exec` - Execute remote command
- `GET /api/ssh/repls` - List user's Repls
- `POST /api/ssh/browse` - Browse remote files
- `POST /api/ssh/read` - Read remote file

### Extension
- `GET /extension.json` - Extension manifest
- `GET /panel` - Main AI panel
- `GET /diff` - Diff viewer panel
- `GET /icon.svg` - Extension icon

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Server**: Uvicorn (async ASGI)
- **Database**: PostgreSQL (asyncpg)
- **Auth**: Authlib, python-jose, passlib, bcrypt
- **AI SDKs**: OpenAI, Anthropic, Google Generative AI
- **Search**: Perplexity API

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Modern CSS with dark theme
- **Icons**: Emoji-based for simplicity
- **State**: localStorage for session persistence

### Infrastructure
- **Deployment**: Replit (uvicorn on port 5000)
- **Environment**: NixOS with Python 3.11
- **Database**: Replit PostgreSQL (Neon-backed)
- **Secrets**: Environment variables

---

## 📊 Current Stats

- **API Endpoints**: 40+
- **AI Tools**: 18 (function-calling)
- **AI Providers**: 3 (OpenAI, Anthropic, Google)
- **AI Models**: 10+ (GPT-4, GPT-5, Claude, Gemini, etc.)
- **Extension Panels**: 2 (Main + Diff)
- **Authentication Methods**: 3 (GitHub OAuth, GitHub PAT, Username/Password)

---

## 🚀 Capabilities

### What RepEditor Can Do:

✅ Edit code in GitHub repos  
✅ Edit code in Replit apps  
✅ Access remote Repls via SSH  
✅ Query and modify databases  
✅ Commit and push to git  
✅ Search the web for info  
✅ Execute shell commands  
✅ Analyze project structure  
✅ Generate code diffs  
✅ Auto-create PRs  
✅ Store persistent memory  
✅ Work as Replit Extension  

### What Makes It Unique:

- **Universal Access**: Works with GitHub repos AND Replit apps
- **Multi-AI**: Choose your preferred AI provider/model
- **Extension Mode**: Add to any Repl workspace
- **Full Automation**: Plan → Diff → Commit → PR in one click
- **Agent-Level Powers**: Same capabilities as Replit Agent/Eidolon

---

## 📝 Environment Variables Required

```bash
DATABASE_URL              # PostgreSQL connection
GITHUB_CLIENT_ID          # GitHub OAuth app
GITHUB_CLIENT_SECRET      # GitHub OAuth secret
OPENAI_API_KEY           # OpenAI (GPT-4, GPT-5)
ANTHROPIC_API_KEY        # Anthropic (Claude)
GOOGLEAQ_API_KEY         # Google (Gemini)
PERPLEXITY_API_KEY       # Web search
APP_BASE_URL             # OAuth callback URL
```

---

## 📚 Documentation

- `README.md` - Project overview
- `replit.md` - Architecture & preferences
- `EXTENSION_SETUP.md` - Extension installation guide
- `EXTENSION_QUICKSTART.md` - Quick reference
- `FEATURES.md` - This file

---

**Built with ❤️ for developers who want AI-powered repo editing everywhere**
