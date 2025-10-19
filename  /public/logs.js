// logs.js
const LOG = document.getElementById("log");
const APP_ORIGIN = "https://dev.melodydashora.dev"; // if you add /api/jobs/stream
try {
  const es = new EventSource(`${APP_ORIGIN}/api/jobs/stream`);
  es.onmessage = (e)=>{ LOG.textContent += `\n${e.data}`; LOG.scrollTop=LOG.scrollHeight; }
  es.onerror   = ()=>{ LOG.textContent += `\n[disconnected]`; }
} catch (e) {
  LOG.textContent = `SSE not available: ${e}`;
}