# Replit Extension Deployment Guide

## ✅ Files Location: `/public` Directory

All extension files are correctly located in the `/public` directory as required by Replit:

```
/public/
├── extension.json       # Extension manifest
├── panel.html          # Main AI panel
├── panel.js            # Panel logic
├── diff.html           # Diff viewer
├── diff.js             # Diff viewer logic
└── icon.svg            # Extension icon
```

## 🎯 URL Mapping

FastAPI routes serve these files at root URLs:

| File in `/public`      | Served at URL    |
|----------------------|------------------|
| `public/extension.json` | `/extension.json` |
| `public/panel.html`     | `/panel.html`     |
| `public/panel.js`       | `/panel.js`       |
| `public/diff.html`      | `/diff.html`      |
| `public/diff.js`        | `/diff.js`        |
| `public/icon.svg`       | `/icon.svg`       |

## ✅ Spec-Compliant Manifest

The `extension.json` follows the exact specification:

```json
{
  "name": "GPT Repository Access",
  "description": "Direct GPT-5 access with full repository control",
  "icon": "/icon.svg",
  "tools": [
    { "handler": "/panel.html", "name": "Vecto Pilot AI", "icon": "/icon.svg" },
    { "handler": "/diff.html", "name": "Diff Viewer", "icon": "/icon.svg" }
  ],
  "scopes": [
    { "name": "read", "reason": "Read any file in your App" },
    { "name": "write-exec", "reason": "Write to files and run shell/commands" },
    { "name": "repldb:read", "reason": "Load cached plans/diffs" },
    { "name": "repldb:write", "reason": "Store cached plans/diffs" },
    { "name": "experimental-api", "reason": "Use experimental fs/process APIs" }
  ],
  "fileHandlers": [
    { "glob": "**/*.{diff,patch}", "handler": "/diff.html", "name": "Diff Viewer" }
  ]
}
```

## 🚀 Ready for Extension Deployment

1. **Files**: All in `/public` directory ✓
2. **Routes**: FastAPI serving from `/public` ✓  
3. **Manifest**: Spec-compliant JSON ✓
4. **Handlers**: Tools & file handlers configured ✓
5. **Scopes**: All 5 required permissions ✓

**Your extension is ready to be loaded!**