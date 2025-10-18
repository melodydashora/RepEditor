#!/usr/bin/env bash
#
# Token Generation Script
# Generates secure 64-character hex tokens for Vecto Pilot authentication
#

set -e

echo "=================================================="
echo "VECTO PILOT - TOKEN GENERATOR"
echo "=================================================="
echo ""
echo "Generating secure 64-hex tokens (32 bytes)..."
echo ""

# Generate tokens
SDK_TOKEN=$(openssl rand -hex 32)
GW_KEY=$(openssl rand -hex 32)
AGENT_TOKEN=$(openssl rand -hex 32)
EIDOLON_TOKEN=$(openssl rand -hex 32)
ASSISTANT_OVERRIDE_TOKEN=$(openssl rand -hex 32)

# Display tokens
echo "✅ Generated tokens:"
echo ""
echo "SDK_TOKEN=$SDK_TOKEN"
echo "GW_KEY=$GW_KEY"
echo "AGENT_TOKEN=$AGENT_TOKEN"
echo "EIDOLON_TOKEN=$EIDOLON_TOKEN"
echo "ASSISTANT_OVERRIDE_TOKEN=$ASSISTANT_OVERRIDE_TOKEN"
echo ""

# Optional: Write to .env.tokens file
if [ "$1" == "--save" ]; then
    cat > .env.tokens << EOF
# Generated tokens - $(date -u +"%Y-%m-%d %H:%M:%S UTC")
SDK_TOKEN=$SDK_TOKEN
GW_KEY=$GW_KEY
AGENT_TOKEN=$AGENT_TOKEN
EIDOLON_TOKEN=$EIDOLON_TOKEN
ASSISTANT_OVERRIDE_TOKEN=$ASSISTANT_OVERRIDE_TOKEN
EOF
    echo "✅ Tokens saved to .env.tokens"
    echo ""
    echo "⚠️  SECURITY NOTICE:"
    echo "   - Add .env.tokens to .gitignore"
    echo "   - Copy tokens to your .env file"
    echo "   - Delete .env.tokens after copying"
    echo ""
fi

echo "=================================================="
echo "USAGE:"
echo "  1. Copy these tokens to your .env file"
echo "  2. Never commit tokens to version control"
echo "  3. Run with --save to write to .env.tokens"
echo "=================================================="
