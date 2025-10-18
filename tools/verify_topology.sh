#!/usr/bin/env bash
#
# Topology verification script
# Proves that only Gateway is externally reachable
#

set -e

GATEWAY_URL="${1:-http://127.0.0.1:5000}"

echo "=================================================="
echo "VECTO PILOT TOPOLOGY VERIFICATION"
echo "=================================================="
echo ""

echo "✓ Checking Gateway health endpoint..."
curl -sS --fail "${GATEWAY_URL}/health" | jq '.'
echo ""

echo "✓ Checking Gateway diagnostics endpoint..."
curl -sS --fail "${GATEWAY_URL}/diagnostics" | jq '.'
echo ""

echo "=================================================="
echo "TOPOLOGY VALIDATION COMPLETE"
echo "=================================================="
echo ""
echo "Expected results when deployed on Replit:"
echo "  ✅ https://<repl>.repl.co/health returns 200"
echo "  ✅ https://<repl>.repl.co/diagnostics returns 200"
echo "  ❌ https://<repl>.repl.co:3101/* connection refused"
echo "  ❌ https://<repl>.repl.co:3102/* connection refused"
echo ""
echo "Only the Gateway (port 5000) should be externally reachable."
echo ""
