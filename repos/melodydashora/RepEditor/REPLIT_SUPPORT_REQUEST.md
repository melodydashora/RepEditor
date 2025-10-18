# Request to Replit Support

## Subject
Request to remove Replit agent overrides for my Repl so my repo-owned Gateway is authoritative

## Body

Please stop applying the Replit platform assistant override for this Repl:
- **Username**: melodydashora
- **Repl**: Vecto-Pilot

I own the repository and run a single public Gateway process that must be the only externally reachable service.

### Repository-Side Evidence and Configuration

1. ✅ I added `.replit-assistant-override.json` with `"enabled": false` to opt out
2. ✅ Gateway binds to `0.0.0.0:5000` and exposes health at `/health` (returns `role: gateway` and ports)
3. ✅ SDK and Agent bind to `127.0.0.1:3101` and `127.0.0.1:3102` respectively and must NOT be reachable publicly

### Acceptance Criteria I Ask Replit to Validate

1. ✅ `curl https://<repl>.repl.co/health` returns HTTP 200 and a JSON body with `"role": "gateway"`
2. ✅ `curl https://<repl>.repl.co/api/diagnostics` returns HTTP 200 with topology information
3. ❌ Ports 3101 and 3102 are NOT reachable from the public internet for this Repl
4. ❌ No Replit assistant/system prompt edits or overrides are injected into the running process

### Verification Commands

```bash
# Gateway health check (should return 200)
curl https://<repl>.repl.co/health | jq '.'

# Diagnostics with topology (should return 200)
curl https://<repl>.repl.co/api/diagnostics | jq '.'

# SDK port check (should connection refused)
curl https://<repl>.repl.co:3101/

# Agent port check (should connection refused)
curl https://<repl>.repl.co:3102/
```

### What I Need

- **Remove** any platform-level assistant overrides for this Repl
- **Ensure** only port 5000 (Gateway) is publicly exposed
- **Block** external access to ports 3101 (SDK) and 3102 (Agent)

If your team prefers, I can provide an SSH session or temporary invite to validate; otherwise please run the checks above and confirm.

Thank you,
Melody (repo owner)

---

## Fallback Plan (if Replit cannot accommodate)

If Replit refuses or cannot disable their agent:

1. **Option A**: Move the authoritative Gateway off-Replit (VPS, Cloud Run, Railway, Fly)
   - Keep the public Gateway there
   - Set the Repl UI to talk to it via `GATEWAY_URL`

2. **Option B**: Create two Repls
   - `gateway-core` (private) 
   - `vecto-ui-python` (public UI)
   - Ask Replit to expose only the UI Repl
   - Point it at the external Gateway

This decouples control and prevents platform override from interfering with Gateway logic.
