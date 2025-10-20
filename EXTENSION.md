# RepEditor - Complete Replit Extension Documentation

## Extension Overview

**RepEditor** is a production-ready Replit Extension that provides AI-powered repository editing with GPT-5, Claude, and Gemini models. The extension includes 5 custom workspace tools, 3 file handlers, and comprehensive permission scopes.

---

## Extension Manifest (extension.json)

### Official Schema Reference

According to Replit's official documentation, the `extension.json` file must follow this structure:

```json
{
  "name": "string (required, 1-60 chars)",
  "description": "string (required, 1-255 chars)",
  "longDescription": "string (optional, supports Markdown)",
  "icon": "string (optional, path to icon file)",
  "tags": ["array of strings (optional)"],
  "coverImages": [{"path": "string", "label": "string"}],
  "website": "string (optional)",
  "authorEmail": "string (optional, public)",
  "tools": [{"handler": "string", "name": "string", "icon": "string"}],
  "fileHandlers": [{"glob": "string", "handler": "string", "name": "string", "icon": "string"}],
  "scopes": [{"name": "ScopeType", "reason": "string"}],
  "background": {"page": "string"}
}
```

### Tool Definition

A **Tool** is a custom UI in the Workspace as a Pane.

**Properties:**
- `handler` (required): Path to the handler file, relative to statically served root
- `name` (optional): Required if more than one tool is registered
- `icon` (optional): Required if more than one tool is registered

### File Handler Definition

A **FileHandler** provides custom UI for specific file types.

**Properties:**
- `glob` (required): Pattern matching files (e.g., `*.svg`)
- `handler` (required): Path to the handler file
- `name` (optional): Required if more than one handler registered
- `icon` (optional): Required if more than one handler registered

### Scope Definition

**Scopes** specify permissions required by the extension.

**Properties:**
- `name` (required): One of the ScopeType values
- `reason` (required): User-facing explanation

**Valid ScopeType Values:**
- `"read"` - Read any file in a Replit App
- `"write-exec"` - Write to any file and execute code/commands
- `"repldb:read"` - Read data from ReplDB key-value store
- `"repldb:write"` - Write/delete keys in ReplDB
- `"experimental-api"` - Use experimental APIs

---

## RepEditor Extension Configuration

### Current Extension Setup

**5 Custom Tools:**
1. AI Assistant (`/gpt-frame.html`) - GPT-5 powered chat interface
2. Repo Fixer (`/panel.html`) - Repository auto-fix with diff generation
3. SQL Viewer (`/sql.html`) - Database inspection tool
4. Logs & Diagnostics (`/logs.html`) - Real-time log viewer
5. Settings (`/config.html`) - Extension configuration panel

**3 File Handlers:**
1. SVG Editor (`*.svg`) - Custom SVG file editor
2. Diff Viewer (`*.diff`) - Unified diff viewer
3. Patch Viewer (`*.patch`) - Patch file handler

**5 Permission Scopes:**
1. `read` - Read files from workspace
2. `write-exec` - Write files and execute commands
3. `repldb:read` - Read from ReplDB
4. `repldb:write` - Write to ReplDB
5. `experimental-api` - Access experimental APIs

**Background Script:**
- Location: `/background.html`
- Purpose: Persistent background process for event handling

---

## API Reference

### Available Replit Extension APIs

#### 1. Initialization API (`init`)
```typescript
import { init } from '@replit/extensions';

const { dispose, status } = await init({ timeout: 5000 });
```

#### 2. Filesystem API (`fs`)
```typescript
import { fs } from '@replit/extensions';

// Read file
const { content } = await fs.readFile('/path/to/file', 'utf8');

// Write file
await fs.writeFile('/path/to/file', content);

// Watch file
const dispose = await fs.watchFile('/path', {
  onChange: (newContent) => console.log(newContent)
}, 'utf8');
```

#### 3. Exec API (`exec`)
```typescript
import { exec } from '@replit/extensions';

// Execute command
const { exitCode, output } = await exec.exec('ls -la', { env: {} });

// Spawn process
const { resultPromise, dispose } = exec.spawn({
  args: ['npm', 'install'],
  env: {},
  onOutput: (output) => console.log(output)
});
```

#### 4. Data API (`data`)
```typescript
import { data } from '@replit/extensions';

// Get current user
const { user } = await data.currentUser({ includePlan: true });

// Get current repl
const { repl } = await data.currentRepl({ includeOwner: true });
```

#### 5. Auth API (`auth`)
```typescript
import { experimental } from '@replit/extensions';
const { auth } = experimental;

// Get auth token
const token = await auth.getAuthToken();

// Authenticate
const { user, installation } = await auth.authenticate();
```

#### 6. Session API (`session`)
```typescript
import { session } from '@replit/extensions';

// Get active file
const activeFile = await session.getActiveFile();

// Watch for file changes
const dispose = session.onActiveFileChange((file) => {
  console.log('Active file:', file);
});
```

#### 7. Messages API (`messages`)
```typescript
import { messages } from '@replit/extensions';

// Show confirmation
const id = await messages.showConfirm('Success!', 3000);

// Show error
await messages.showError('Something went wrong', 5000);

// Hide message
await messages.hideMessage(id);
```

#### 8. ReplDB API (`replDb`)
```typescript
import { replDb } from '@replit/extensions';

// Set value
await replDb.set({ key: 'myKey', value: 'myValue' });

// Get value
const value = await replDb.get({ key: 'myKey' });

// List keys
const { keys } = await replDb.list({ prefix: 'my' });

// Delete key
await replDb.del({ key: 'myKey' });
```

#### 9. Commands API (`commands`)
```typescript
import { commands } from '@replit/extensions';

// Add command
commands.add({
  id: 'my-command',
  label: 'My Command',
  run: async () => {
    console.log('Command executed');
  }
});
```

#### 10. Debug API (`debug`)
```typescript
import { debug } from '@replit/extensions';

// Log info
await debug.info('Information', { data: 'value' });

// Log warning
await debug.warn('Warning message', { code: 123 });

// Log error
await debug.error('Error occurred', { stack: 'trace' });
```

---

## Publishing Your Extension

### Prerequisites

1. **Icon Design**
   - Use the [Figma template](https://www.figma.com/community/file/1220063901895293170)
   - Or use the Icon Generator Extension
   - SVG format preferred
   - Must be clean, visible, and memorable

2. **Build Configuration**
   - For HTML/CSS/JS: Build command = `" "` (single space), Output = `.`
   - For Vite: Build command = `npm run build`, Output = `dist`
   - For Next.js: Build command = `npm run export`, Output = `out`

### Publishing Steps

1. **Clear Extension Cache**
   - Go to Extensions → DevTools
   - Click ⋮ menu → "Clear Local Extension Cache"

2. **Load Extension Locally**
   - Click "Load Locally" in DevTools
   - Verify extension name appears (not "Unnamed Extension")

3. **Create Release**
   - Configure tab:
     - Build command: `npm run build` (or blank for static)
     - Output folder: `public`
   - Add listing details:
     - Title: "GPT Repository Access"
     - Icon: `/icon.svg`
     - Tags: AI, Git, Repository, Assistant
     - Background page: `/background.html`
   - Click **Publish** (Public)

4. **Review Process**
   - Wait for Replit staff review
   - Extension will be manually verified before appearing in store

### Common Issues

**Issue: "Expected union value" error**
- **Cause**: Extension.json schema mismatch
- **Fix**: Ensure all tools have `handler`, `name`, `icon` fields
- **Fix**: Ensure all scopes are objects with `name` and `reason`

**Issue: Backend server not working**
- **Cause**: Extensions must be statically served
- **Fix**: Separate server and client into different Replit Apps

**Issue: Timeout error**
- **Cause**: Opening extension in Preview pane instead of Extension pane
- **Fix**: Use Extension Devtools, not Preview
- **Fix**: Click Reload icon in extension tab

**Issue: Extension not loading**
- **Cause**: Cached old version
- **Fix**: Clear Local Extension Cache and reload

---

## Backend API Endpoints

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
- `GET /api/assistant/verify-override` - Verify assistant override token

### AI Autofix
- `/api/ai/plan` - GPT-5 analyzes repo and creates fix plan
- `/api/ai/diff` - Codex generates unified diff patches
- `/api/ai/apply` - Auto-commits, pushes branch, opens PR
- `/api/ai/autofix` - One-click: plan → diff → apply → PR
- `/api/ai/tree` - Browse GitHub repo file tree
- `/api/ai/file` - Read file contents from GitHub

### SSH Access
- `/api/ssh/keygen` - Generate SSH keypairs
- `/api/ssh/keys` - List stored SSH keys
- `/api/ssh/connect` - Get SSH connection details
- `/api/ssh/exec` - Execute commands on remote Repls
- `/api/ssh/repls` - List available Replit apps
- `/api/ssh/browse` - Browse files in remote Repls
- `/api/ssh/read` - Read file contents from remote Repls

---

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

---

## Tech Stack

- **Backend**: FastAPI, Python 3.11, Uvicorn
- **Database**: PostgreSQL with asyncpg
- **Authentication**: GitHub OAuth + username/password
- **AI Providers**: OpenAI (GPT-4, GPT-5), Anthropic (Claude), Google (Gemini)
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Extension Framework**: Replit Extensions API

---

## Development Workflow

1. **Local Development**
   - Run: `python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload`
   - Access: `http://localhost:5000`

2. **Testing Extension**
   - Use Extension Devtools (not Preview pane)
   - Load locally from running server
   - Clear cache between tests

3. **Deployment**
   - Configure build: Output folder = `public`
   - Publish extension
   - Wait for staff review

---

## Support & Resources

- **Official Docs**: [https://docs.replit.com/extensions](https://docs.replit.com/extensions)
- **Extension Store**: [https://replit.com/extensions](https://replit.com/extensions)
- **Icon Template**: [Figma Community](https://www.figma.com/community/file/1220063901895293170)
- **CLUI**: Press CMD/CTRL + K for command bar

---

## License & Credits

- **Project**: RepEditor (AI-Powered Repository Editor)
- **Repository**: git@github.com:melodydashora/RepEditor.git
- **Website**: https://dev.melodydashora.dev
- **Author Email**: bot@vectopilot.com
- **Investment**: $400+ and 18+ hours of development
- **Status**: Production-Ready, Awaiting Review
