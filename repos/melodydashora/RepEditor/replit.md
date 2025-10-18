# RepEditor - AI-Powered Repository Editor

## Overview
RepEditor is a unified AI Assistant Builder platform that enables users to create custom AI assistants with:
- Full repository access and code editing capabilities
- Dynamic provider/model selection across OpenAI, Anthropic, and Gemini
- GitHub OAuth authentication and repository management
- Real-time chat interface with streaming responses
- Support for both function-calling models and specialized models

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

## Environment Variables
Required secrets:
- `DATABASE_URL` - PostgreSQL connection string
- `GITHUB_CLIENT_ID` - GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET` - GitHub OAuth app secret
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLEAQ_API_KEY` - Google AI API key
- `APP_BASE_URL` - Application base URL for OAuth callbacks

## Recent Updates

### October 18, 2025
- Implemented GitHub OAuth authentication with Authlib
- Added repository cloning and file browsing system
- Created dual authentication (GitHub + username/password)
- Built session management with 30-day expiration
- Added git operations (commit, push, config)
- Removed all rideshare-specific content to focus on AI assistant builder
- Enhanced settings modal with dual repository support (GitHub + Replit)
- Added disabled state for dropdowns until authentication succeeds
- Implemented proper app/repo listing after authentication

## Repository
- **GitHub**: git@github.com:melodydashora/RepEditor.git
- **Project Name**: RepEditor (AI-Powered Repository Editor)

## User Preferences
- Focus on building the best AI assistant framework
- Clean, modern UI with minimal dependencies
- Security-first approach (no credentials in browser)
