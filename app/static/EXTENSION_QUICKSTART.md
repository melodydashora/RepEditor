# 🚀 Vecto Pilot AI Extension - Quickstart

## What is this?

A **Replit Extension** that adds GPT-5 with full repository access to your workspace sidebar.

Think: **Replit Agent, but for ANY workspace**.

---

## 📦 What You Get

### Main Panel: "Vecto Pilot AI"
- **GPT-5** (medium reasoning, 16K tokens)
- Full repository file access (read/write)
- Database operations (PostgreSQL)
- Git operations (commit, push, diff, status)
- Web search (Perplexity)
- Shell command execution
- Memory storage
- Workspace analysis

### Diff Viewer Panel
- Click `.diff` or `.patch` files
- Opens in dedicated viewer

---

## 🎯 Setup (3 Minutes)

### Step 1: Extensions UI

Go to **Replit Extensions** → Add:

**Permissions:**
- ✅ Read files
- ✅ Write & Execute  
- ✅ ReplDB (read + write)
- ✅ Experimental APIs
- ✅ Network

**Tools (add 2):**

1. **Vecto Pilot AI**
   - URL: `/panel`
   - Icon: `/icon.svg`

2. **Diff Viewer**
   - URL: `/diff`
   - Icon: `/icon.svg`

**File Handler (optional):**
- URL: `/diff`
- Extensions: `diff,patch`

Click **Save Changes** → **Load Locally**

### Step 2: Any Workspace

In ANY Repl's `.replit` file, add:

```toml
[extension]
isExtension = true
extensionID = "gpt-repo-access"
```

Reload the Repl → Extension appears in right sidebar!

---

## 🔥 Features

### 18 AI Tools

**File System:**
- `read_file` - Read any file
- `write_file` - Write/edit files
- `list_directory` - Browse directories
- `search_files` - Find files by name
- `grep_code` - Search code content
- `get_repo_structure` - Full tree view

**Git:**
- `git_status` - Check status
- `git_diff` - View changes
- `git_commit` - Commit with message
- `git_push` - Push to remote

**Database:**
- `sql_query` - SELECT queries
- `sql_execute` - INSERT/UPDATE/DELETE
- `get_database_schema` - Inspect tables

**System:**
- `execute_command` - Run shell commands
- `analyze_workspace` - Project overview
- `web_search` - Perplexity search
- `get_memory` / `write_memory` - Persistent storage

---

## 💡 Example Usage

**Ask GPT:**

> "Read app/main.py and fix any bugs"

> "Add a new API endpoint for user authentication"

> "Commit all changes with message 'Add auth system'"

> "Search the web for FastAPI best practices"

> "Query the database for all users"

---

## 🌐 Endpoints

All served from **https://dev.melodydashora.dev**:

- `/extension.json` - Manifest
- `/panel` - Main AI panel
- `/panel.html` / `/panel.js` - Panel files
- `/diff` - Diff viewer  
- `/diff.html` / `/diff.js` - Diff files
- `/icon.svg` - Icon
- `/api/chat/frame` - GPT-5 backend

---

## 🔧 Advanced: FS Bridge

Your app can access the **current Repl's filesystem** via postMessage:

```javascript
// Read file from current workspace
parent.postMessage({
  type: "fs.read",
  path: "app/main.py",
  reqId: "1"
}, "*");

// Write file
parent.postMessage({
  type: "fs.write",
  path: "config.json",
  content: '{"key": "value"}',
  reqId: "2"
}, "*");

// Execute command
parent.postMessage({
  type: "proc.exec",
  cmd: "git status",
  reqId: "3"
}, "*");
```

Listen for responses:

```javascript
window.addEventListener("message", (ev) => {
  if (ev.data.type === "fs.read.ok") {
    console.log("File:", ev.data.data);
  }
});
```

---

## ✅ You're Done!

The extension now works in **any Repl** with the `.replit` config.

No code changes needed in target projects - just add the config and reload!
