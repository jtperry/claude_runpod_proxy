#!/bin/bash
# Copyright 2026 JT Perry
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

# Load .env safely
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "❌ Error: .env file missing."
    exit 1
fi

# 0. Check for Local LLM Server
# Probe Ollama (11434) or standard OpenAI-compatible ports (8000)
DETECTED_LOCAL_URL=""
if curl -s http://localhost:11434/api/tags > /dev/null; then
    DETECTED_LOCAL_URL="http://localhost:11434"
    LOCAL_TYPE="ollama"
elif curl -s http://localhost:8000/v1/models > /dev/null; then
    DETECTED_LOCAL_URL="http://localhost:8000"
    LOCAL_TYPE="openai-compatible"
fi

# Determine if we should use local based on detection or .env
if [ -n "$DETECTED_LOCAL_URL" ] || [ -n "$LOCAL_API_BASE" ]; then
    ACTUAL_LOCAL_URL="${LOCAL_API_BASE:-$DETECTED_LOCAL_URL}"
    echo "🏠 Local LLM detected at $ACTUAL_LOCAL_URL"
    read -p "❓ Use local model instead of spinning up RunPod? (y/n): " use_local
    
    if [[ $use_local == [yY] ]]; then
        # Use .env default or fall back to the cloud MODEL_ID
        DEFAULT_LOCAL_NAME="${LOCAL_MODEL_ID:-$MODEL_ID}"
        read -p "📝 Enter local model name (default: $DEFAULT_LOCAL_NAME): " input_name
        
        export LOCAL_MODEL_ID="${input_name:-$DEFAULT_LOCAL_NAME}"
        export LOCAL_API_BASE="$ACTUAL_LOCAL_URL"
        export USE_LOCAL_ONLY=true
    fi
fi

# 1. Provision RunPod (Skip if using local only)
EID=""
if [ "$USE_LOCAL_ONLY" != "true" ]; then
    EID=$(uv run manage_pod.py up | tail -n 1)
    if [[ -z "$EID" || "$EID" == *"Aborted"* ]]; then exit 0; fi
    export RUNPOD_ENDPOINT_ID=$EID
fi

# 2. Start LiteLLM Proxy
echo "🚀 Starting LiteLLM Proxy..."
export LITELLM_MASTER_KEY="${ANTHROPIC_API_KEY:-sk-admin-key}"
export EXPERIMENTAL_UI_LOGIN="True"

# LiteLLM stays in the mix and manages both cloud and local backends
uv run litellm --config config.yaml --port 4000 > /dev/null 2>&1 &
LPID=$!

cleanup() {
    echo -e "\n-----------------------------------"
    if [ -n "$EID" ]; then
        echo "📊 Total Session Cost: $(uv run manage_pod.py cost)"
        echo "-----------------------------------"
        read -p "🛑 Delete Pod $EID? (y/n): " confirm
        [[ $confirm == [yY] ]] && uv run manage_pod.py down $EID
    fi
    kill $LPID 2>/dev/null || true
}
trap cleanup EXIT

# 3. Intelligent Wait
if [ "$USE_LOCAL_ONLY" == "true" ]; then
    echo "✅ Using local backend ($LOCAL_MODEL_ID). No RunPod wait required."
else
    uv run manage_pod.py wait $EID
fi

# 4. Ready State
echo -e "\n✅ Ready! Traffic managed by LiteLLM."
echo "🖥️  LiteLLM Console: http://0.0.0.0:4000/