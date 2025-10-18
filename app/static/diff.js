import { experimental } from "@replit/extensions";
const { fs } = experimental ?? {};
const out = document.getElementById("out");

async function openPathFromQuery() {
  const u = new URL(location.href);
  const p = u.searchParams.get("path");
  if (!p || !fs?.readFile) return;
  const buf = await fs.readFile(p);
  out.value = new TextDecoder().decode(buf);
}
openPathFromQuery();
