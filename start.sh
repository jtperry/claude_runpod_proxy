#!/bin/bash
# Copyright 2026 JT Perry
# Licensed under Apache 2.0

set -e

# Load .env safely without triggering set -e on empty lines
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "❌ Error: .env file missing."
    exit 1
fi

# 1. Provision / Discovery
# Use 2>/dev/null to keep the EID capture clean
EID=$(uv run manage_pod.py up | tail -n 1)

if [[ -z "$EID" || "$EID" == *"Aborted"* ]]; then
    exit 0
fi

export RUNPOD_ENDPOINT_ID=$EID

# 2. Start Proxy
echo "🚀 Starting LiteLLM Proxy..."
uv run litellm --config config.yaml --port 4000 > /dev/null 2>&1 &
LPID=$!
trap "kill $LPID 2>/dev/null || true" EXIT

# 3. Wait for Worker
echo "⏳ Waiting for cold start (loading $MODEL_ID)..."
until curl -s http://0.0.0.0:4000/v1/models > /dev/null; do 
    sleep 5
done

# 4. Launch Claude Code
echo -e "\n✅ Ready! Session Cost: $(uv run manage_pod.py cost)"
ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL \
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
ANTHROPIC_MODEL=$ANTHROPIC_MODEL \
claude

# 5. Shutdown
kill $LPID
echo -e "\n-----------------------------------"
echo "📊 Total Cost: $(uv run manage_pod.py cost)"
echo "-----------------------------------"
read -p "🛑 Delete Pod $EID? (y/n): " confirm
[[ $confirm == [yY] ]] && uv run manage_pod.py down $EID