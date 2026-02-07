#!/bin/bash

# Load .env
export $(grep -v '^#' .env | xargs)

# 1. Management Phase
ENDPOINT_ID=$(uv run manage_pod.py up | tail -n 1)
export RUNPOD_ENDPOINT_ID=$ENDPOINT_ID

# 2. Proxy Phase
echo "🚀 Starting LiteLLM Proxy for Endpoint: $ENDPOINT_ID"
uv run litellm --config config.yaml --port 4000 &
PROXY_PID=$!

# Wait for proxy
sleep 3

# 3. Work Phase
echo "💻 Launching Claude Code..."
ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL \
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
ANTHROPIC_MODEL=$ANTHROPIC_MODEL \
claude

# 4. Cleanup Phase
kill $PROXY_PID
echo ""
read -p "❓ Shutdown and DELETE this RunPod endpoint to stop costs? (y/n): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    uv run manage_pod.py down $ENDPOINT_ID
else
    echo "Keep-alive: Endpoint $ENDPOINT_ID is still active on RunPod."
fi