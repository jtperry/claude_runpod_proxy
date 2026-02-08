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

# 1. Provision / Discovery
EID=$(uv run manage_pod.py up | tail -n 1)
if [[ -z "$EID" || "$EID" == *"Aborted"* ]]; then exit 0; fi

export RUNPOD_ENDPOINT_ID=$EID

# 2. Start Proxy
echo "🚀 Starting LiteLLM Proxy..."
uv run litellm --config config.yaml --port 4000 > /dev/null 2>&1 &
LPID=$!

cleanup() {
    echo -e "\n-----------------------------------"
    echo "📊 Total Session Cost: $(uv run manage_pod.py cost)"
    echo "-----------------------------------"
    read -p "🛑 Delete Pod $EID? (y/n): " confirm
    [[ $confirm == [yY] ]] && uv run manage_pod.py down $EID
    kill $LPID 2>/dev/null || true
}
trap cleanup EXIT

# 3. Intelligent Wait for Worker
# Polling the RunPod API to see when the model is actually loaded
uv run manage_pod.py wait $EID

# 4. Ready State
echo -e "\n✅ Ready! All traffic routed to $MODEL_ID."
echo "👉 VS Code: Run 'code .' in a second terminal now."
echo "🚀 Launching Claude CLI in 5 seconds..."
sleep 5

# 5. Launch Claude Code
export ANTHROPIC_BASE_URL="http://0.0.0.0:4000"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
# Note: Claude will ask to use the custom API key; answer "Yes"
claude