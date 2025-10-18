// Vecto Pilot AI - Extension Panel Script
const APP_ORIGIN = window.location.origin;
const IFRAME_URL = `${APP_ORIGIN}/api/chat/frame`;

const app = document.getElementById("app");
const statusEl = document.getElementById("status");
const loadingEl = document.getElementById("loading");

// Open full app in new window
document.getElementById("open").onclick = () => {
  window.open(APP_ORIGIN, "_blank", "noopener");
};

// Load GPT frame
app.onload = () => {
  loadingEl.style.display = "none";
};
app.src = IFRAME_URL;

// Import Replit experimental APIs (if available)
import("@replit/extensions").then(({ experimental }) => {
  const { auth, fs, process: proc } = experimental ?? {};
  
  // Authenticate and show user info
  (async () => {
    try {
      if (auth) {
        const { user } = await auth.authenticate();
        if (user?.username) {
          statusEl.textContent = `● ${user.username}`;
          statusEl.style.background = "rgba(102,126,234,0.15)";
          statusEl.style.borderColor = "rgba(102,126,234,0.3)";
          statusEl.style.color = "#667EEA";
        }
        
        // Send user context to iframe
        const jwt = await auth.getAuthToken().catch(() => null);
        app.contentWindow?.postMessage({ 
          type: "replit-user", 
          user, 
          jwt 
        }, APP_ORIGIN);
      }
    } catch (err) {
      console.log("[Vecto] Auth not available:", err);
    }
  })();

  // Direct Repl FS access bridge
  if (fs && proc) {
    // Helper functions for file operations
    async function readFile(path) {
      const buf = await fs.readFile(path);
      return new TextDecoder().decode(buf);
    }

    async function writeFile(path, content) {
      await fs.writeFile(path, new TextEncoder().encode(content));
    }

    async function listDir(path = ".") {
      const entries = await fs.readdir(path);
      return entries;
    }

    async function run(cmd) {
      const { stdout, stderr, code } = await proc.exec({ 
        cmd: ["bash", "-lc", cmd] 
      });
      return { 
        stdout: new TextDecoder().decode(stdout || new Uint8Array()),
        stderr: new TextDecoder().decode(stderr || new Uint8Array()),
        code 
      };
    }

    // Listen for requests from iframe
    window.addEventListener("message", async (ev) => {
      if (new URL(APP_ORIGIN).origin !== ev.origin) return;
      const { type, path, content, cmd, reqId } = ev.data || {};
      
      try {
        switch(type) {
          case "fs.read":
            const data = await readFile(path);
            app.contentWindow?.postMessage({ 
              type: "fs.read.ok", 
              reqId, 
              data 
            }, APP_ORIGIN);
            break;
            
          case "fs.write":
            await writeFile(path, content);
            app.contentWindow?.postMessage({ 
              type: "fs.write.ok", 
              reqId 
            }, APP_ORIGIN);
            break;
            
          case "fs.list":
            const entries = await listDir(path);
            app.contentWindow?.postMessage({ 
              type: "fs.list.ok", 
              reqId, 
              entries 
            }, APP_ORIGIN);
            break;
            
          case "proc.exec":
            const out = await run(cmd);
            app.contentWindow?.postMessage({ 
              type: "proc.exec.ok", 
              reqId, 
              out 
            }, APP_ORIGIN);
            break;
        }
      } catch (e) {
        app.contentWindow?.postMessage({ 
          type: `${type}.err`, 
          reqId, 
          error: String(e) 
        }, APP_ORIGIN);
      }
    });
    
    // Notify iframe that FS bridge is ready
    setTimeout(() => {
      app.contentWindow?.postMessage({ 
        type: "replit-extension-ready", 
        capabilities: {
          fs: true,
          proc: true,
          auth: !!auth
        }
      }, APP_ORIGIN);
    }, 1000);
  } else {
    // No FS access - still notify iframe
    setTimeout(() => {
      app.contentWindow?.postMessage({ 
        type: "replit-extension-ready", 
        capabilities: {
          fs: false,
          proc: false,
          auth: false
        }
      }, APP_ORIGIN);
    }, 1000);
  }
}).catch(() => {
  console.log("[Vecto] Running without Replit APIs");
  statusEl.textContent = "● GPT-5 Ready";
});