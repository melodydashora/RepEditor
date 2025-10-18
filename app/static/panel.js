// Embed your hosted app
const APP_ORIGIN = window.location.origin;
const IFRAME_URL = `${APP_ORIGIN}/api/chat/frame`;

const app = document.getElementById("app");
const ctxEl = document.getElementById("ctx");
document.getElementById("open").onclick = () => window.open(APP_ORIGIN, "_blank", "noopener");
app.src = IFRAME_URL;

// Replit experimental APIs
import { experimental } from "@replit/extensions";
const { auth, fs, process } = experimental ?? {};

// show user id (nice-to-have)
(async () => {
  try {
    if (auth) {
      const { user } = await auth.authenticate();
      ctxEl.textContent = `replit:${user?.id ?? "unknown"}`;
      const jwt = await auth.getAuthToken().catch(() => null);
      app.contentWindow?.postMessage({ type: "replit-user", user, jwt }, APP_ORIGIN);
    } else {
      ctxEl.textContent = "extension";
    }
  } catch { ctxEl.textContent = "extension"; }
})();

// FS/proc bridge so your iframe can read/write current Repl if desired
window.addEventListener("message", async (ev) => {
  if (new URL(APP_ORIGIN).origin !== ev.origin) return;
  const { type, path, content, cmd, reqId } = ev.data || {};
  try {
    if (type === "fs.read" && fs?.readFile) {
      const buf = await fs.readFile(path);
      const data = new TextDecoder().decode(buf);
      app.contentWindow?.postMessage({ type: "fs.read.ok", reqId, data }, APP_ORIGIN);
    } else if (type === "fs.write" && fs?.writeFile) {
      await fs.writeFile(path, new TextEncoder().encode(content));
      app.contentWindow?.postMessage({ type: "fs.write.ok", reqId }, APP_ORIGIN);
    } else if (type === "proc.exec" && process?.exec) {
      const r = await process.exec({ cmd: ["bash","-lc", cmd] });
      const out = {
        stdout: new TextDecoder().decode(r.stdout || new Uint8Array()),
        stderr: new TextDecoder().decode(r.stderr || new Uint8Array()),
        code: r.code
      };
      app.contentWindow?.postMessage({ type: "proc.exec.ok", reqId, out }, APP_ORIGIN);
    }
  } catch (e) {
    app.contentWindow?.postMessage({ type: `${type}.err`, reqId, error: String(e) }, APP_ORIGIN);
  }
});

// Tell your app it's running inside the extension
app.addEventListener("load", () => {
  app.contentWindow?.postMessage({ type: "replit-extension-context", payload: { isExtension: true } }, APP_ORIGIN);
});
