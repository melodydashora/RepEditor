// --- CONFIG ---
const APP_ORIGIN = "https://dev.melodydashora.dev"; // your hosted UI
const IFRAME_URL = `${APP_ORIGIN}/?embed=1`;

const app  = document.getElementById("app");
const ctx  = document.getElementById("ctx");
document.getElementById("open").onclick = () => window.open(APP_ORIGIN, "_blank", "noopener");
app.src = IFRAME_URL;

// Try to use Replit Extensions API if available; degrade gracefully if not.
let ext = null;
(async () => {
  try { ext = await import("@replit/extensions"); }
  catch { try { ext = await import("https://esm.sh/@replit/extensions@latest"); } catch {} }

  // Identity (nice-to-have; not required for Git flow)
  try {
    const { experimental } = ext || {};
    const { auth } = experimental || {};
    if (auth?.authenticate) {
      const { user } = await auth.authenticate();
      ctx.textContent = `replit:${user?.id ?? "unknown"}`;
      const jwt = await auth.getAuthToken().catch(() => null);
      app.contentWindow?.postMessage({ type: "replit-user", user, jwt }, APP_ORIGIN);
    } else {
      ctx.textContent = "extension";
    }
  } catch { ctx.textContent = "extension"; }
})();

// FS/exec bridge so your iframe can touch the CURRENT Repl when allowed.
// Your hosted app can still use GitHub PR flow for any repo (recommended).
window.addEventListener("message", async (ev) => {
  if (new URL(APP_ORIGIN).origin !== ev.origin) return;
  const { type, path, content, cmd, reqId } = ev.data || {};
  try {
    const { experimental } = ext || {};
    const { fs, process } = experimental || {};
    if (type === "fs.read" && fs?.readFile) {
      const buf = await fs.readFile(path);
      app.contentWindow?.postMessage({ type:"fs.read.ok", reqId, data:new TextDecoder().decode(buf) }, APP_ORIGIN);
    } else if (type === "fs.write" && fs?.writeFile) {
      await fs.writeFile(path, new TextEncoder().encode(content));
      app.contentWindow?.postMessage({ type:"fs.write.ok", reqId }, APP_ORIGIN);
    } else if (type === "proc.exec" && process?.exec) {
      const r = await process.exec({ cmd:["bash","-lc",cmd] });
      const out = {
        stdout: new TextDecoder().decode(r.stdout||new Uint8Array()),
        stderr: new TextDecoder().decode(r.stderr||new Uint8Array()),
        code:   r.code
      };
      app.contentWindow?.postMessage({ type:"proc.exec.ok", reqId, out }, APP_ORIGIN);
    }
  } catch (e) {
    app.contentWindow?.postMessage({ type: `${ev.data?.type}.err`, reqId, error: String(e) }, APP_ORIGIN);
  }
});

// Tell your app it's embedded
app.addEventListener("load", () => {
  app.contentWindow?.postMessage({ type:"replit-extension-context", payload:{ isExtension:true } }, APP_ORIGIN);
});