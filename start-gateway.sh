#!/usr/bin/env bash
#
# Gateway startup script
# Enforces explicit configuration and topology validation
#

set -e

# Explicit Gateway configuration (public-facing)
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-5000}"

# Explicit SDK configuration (internal)
export SDK_HOST="${SDK_HOST:-127.0.0.1}"
export SDK_PORT="${SDK_PORT:-3101}"

# Explicit Agent configuration (internal)
export AGENT_HOST="${AGENT_HOST:-127.0.0.1}"
export AGENT_PORT="${AGENT_PORT:-3102}"

# AI Model configuration
export ASSISTANT_MODEL="${ASSISTANT_MODEL:-gpt-5}"
export MODEL_PROVIDER="${MODEL_PROVIDER:-openai}"

echo "=================================================="
echo "VECTO PILOT GATEWAY - Starting"
echo "=================================================="
echo "Gateway: $HOST:$PORT (public)"
echo "SDK:     $SDK_HOST:$SDK_PORT (internal)"
echo "Agent:   $AGENT_HOST:$AGENT_PORT (internal)"
echo "Model:   $ASSISTANT_MODEL ($MODEL_PROVIDER)"
echo "=================================================="
echo ""

# Run startup validation checks
python3 -m app.startup_checks

# Start FastAPI Gateway
exec uvicorn app.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --reload
