// GPT Repository Access Extension Panel
const APP_ORIGIN = window.location.origin;
const IFRAME_URL = `/api/chat/frame`;

const app = document.getElementById("app");
const ctxEl = document.getElementById("ctx");

// Open full app in new window
document.getElementById("open").onclick = () => window.open(APP_ORIGIN, "_blank", "noopener");

// Load GPT frame
app.src = IFRAME_URL;

// Optional: identify the current Replit user
import("@replit/extensions").then(({ experimental }) => {
  const { auth, fs, process: proc } = experimental ?? {};
  
  (async () => {
    try {
      if (auth) {
        const { user } = await auth.authenticate();
        ctxEl.textContent = `GPT-5 • ${user?.username ?? "user"}`;
        ctxEl.classList.add("status");
        
        // Send user context to iframe
        const jwt = await auth.getAuthToken().catch(() => null);
        app.contentWindow?.postMessage({ 
          type: "replit-user", 
          user, 
          jwt 
        }, APP_ORIGIN);
      }
    } catch (err) {
      console.log("[Extension] Auth unavailable:", err);
      ctxEl.textContent = "GPT-5 Ready";
    }
  })();

  // Direct Repl FS access
  if (fs && proc) {
    // Helper functions for file operations
    async function readFile(path) {
      const buf = await fs.readFile(path);
      return new TextDecoder().decode(buf);
    }

    async function writeFile(path, content) {
      await fs.writeFile(path, new TextEncoder().encode(content));
    }

    async function run(cmd) {
      const { stdout, stderr, code } = await proc.exec({ cmd: ["bash", "-lc", cmd] });
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
        if (type === "fs.read") {
          const data = await readFile(path);
          app.contentWindow?.postMessage({ 
            type: "fs.read.ok", 
            reqId, 
            data 
          }, APP_ORIGIN);
        } else if (type === "fs.write") {
          await writeFile(path, content);
          app.contentWindow?.postMessage({ 
            type: "fs.write.ok", 
            reqId 
          }, APP_ORIGIN);
        } else if (type === "proc.exec") {
          const out = await run(cmd);
          app.contentWindow?.postMessage({ 
            type: "proc.exec.ok", 
            reqId, 
            out 
          }, APP_ORIGIN);
        }
      } catch (e) {
        app.contentWindow?.postMessage({ 
          type: `${type}.err`, 
          reqId, 
          error: String(e) 
        }, APP_ORIGIN);
      }
    });
  }

  // Pass extension context to app
  app.addEventListener("load", () => {
    app.contentWindow?.postMessage(
      { 
        type: "replit-extension-context", 
        payload: { 
          isExtension: true,
          hasFS: !!fs,
          hasProc: !!proc
        } 
      },
      APP_ORIGIN
    );
  });
}).catch(() => {
  console.log("[Extension] Running without Replit APIs");
  ctxEl.textContent = "GPT-5 Ready";
});
