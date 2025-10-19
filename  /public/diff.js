// diff.js
let ext=null; try{ext=await import("@replit/extensions")}catch{}
const { experimental } = ext || {}; const { fs } = experimental || {};
const out = document.getElementById("out");

async function loadByQuery(){
  const path = new URL(location.href).searchParams.get("path");
  if (!path || !fs?.readFile) return;
  const buf = await fs.readFile(path);
  out.value = new TextDecoder().decode(buf);
}
loadByQuery();
