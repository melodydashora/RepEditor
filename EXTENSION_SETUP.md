# Replit Extension Setup Guide

This document explains how to activate the **Vecto Pilot AI** extension in any Replit workspace.

## 📋 Files Included

All extension files are served from this app:

- `extension.json` - Extension manifest
- `panel.html` - Main AI panel UI
- `panel.js` - Panel logic with FS bridge
- `diff.html` - Diff viewer UI
- `diff.js` - Diff viewer logic
- `icon.svg` - Extension icon

## 🚀 Quick Setup (3 Steps)

### Step 1: Add to `.replit` file

In ANY Repl where you want the extension, add:

```toml
[extension]
isExtension = true
extensionID = "gpt-repo-access"
```

### Step 2: Load Extension in UI

1. Go to Extensions UI in your Replit account
2. Click **"New Extension"** or edit existing one
3. Configure the following:

#### Permission Scopes (enable all):
- ✅ Read files
- ✅ Write & Execute
- ✅ ReplDB Read
- ✅ ReplDB Write
- ✅ Experimental APIs
- ✅ Network

#### Tools → Add Two Tools:

**Tool A - Main Panel:**
- Name: `Vecto Pilot AI`
- URL Path: `/panel`
- Icon: `/icon.svg`

**Tool B - Diff Viewer:**
- Name: `Diff Viewer`
- URL Path: `/diff`
- Icon: `/icon.svg`

#### File Handlers (optional):
- URL Path: `/diff`
- Extensions: `diff,patch`

### Step 3: Load Locally

1. Click **"Save Changes"**
2. Click **"Load Locally"** (or reload your Repl)
3. Open right sidebar → **Vecto Pilot AI** should appear!

## 🎯 What You Get

### Main Panel Features:
- **GPT-5** with full repository access
- Read/write any file in current Repl
- Execute shell commands
- Query PostgreSQL database
- Commit and push to git
- Web search (Perplexity)
- Workspace analysis

### Diff Viewer:
- Click any `.diff` or `.patch` file
- Opens in dedicated viewer pane

## 🔧 Advanced: FS Bridge

Your hosted app can call the Repl's filesystem:

```javascript
// From inside the iframe
parent.postMessage({ 
  type: "fs.read", 
  path: "app/main.py", 
  reqId: "1" 
}, "*");

// Listen for response
window.addEventListener("message", (ev) => {
  if (ev.data.type === "fs.read.ok" && ev.data.reqId === "1") {
    console.log("File content:", ev.data.data);
  }
});
```

Available operations:
- `fs.read` - Read file from current Repl
- `fs.write` - Write file to current Repl
- `proc.exec` - Execute command in current Repl

## 📍 Extension URLs

All served from this app (https://dev.melodydashora.dev):
- `/extension.json` - Manifest
- `/panel` - Main AI panel
- `/diff` - Diff viewer
- `/icon.svg` - Icon

## 💡 How It Works

1. **Extension runs in Replit workspace sidebar** (like Spaces, Console, etc.)
2. **Embeds your hosted app** (`/api/chat/frame`) in an iframe
3. **Bridges Repl APIs** so the iframe can access current workspace files
4. **GPT-5 backend** provides full AI capabilities via your hosted API

This gives you **Agent-level powers in any Repl** without modifying their code!
