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

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RUNPOD_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")
REST_URL = "https://api.runpod.ai/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def get_existing_pod():
    """Checks for an existing Claude-Auto-Pod."""
    r = requests.get(f"{REST_URL}/endpoints", headers=HEADERS)
    endpoints = r.json()
    for ep in endpoints:
        if ep.get("name") == "Claude-Auto-Pod":
            return ep.get("id")
    return None

def up():
    """Provisions a new pod or returns an existing one."""
    existing_id = get_existing_pod()
    if existing_id:
        use_existing = input(f"👉 Use existing pod {existing_id}? (y/n): ")
        if use_existing.lower() == 'y':
            return existing_id

    # GPU logic based on MODEL_ID
    gpu_type = "AMPERE_A100_80" # Default for Qwen3-Coder-Next
    
    payload = {
        "name": "Claude-Auto-Pod",
        "imageName": "runpod/worker-v1-vllm",
        "gpuIds": gpu_type,
        "handler": "vllm",
        "workersMin": 0,
        "workersMax": 1,
        "idleTimeout": 300,
        "env": {
            "MODEL_ID": MODEL_ID,
            "HF_TOKEN": os.getenv("HF_TOKEN")
        }
    }
    
    r = requests.post(f"{REST_URL}/endpoints", headers=HEADERS, json=payload)
    return r.json().get("id")

def wait(eid):
    """Polls the endpoint until at least one worker is warm (IDLE or RUNNING)."""
    print(f"⏳ Monitoring Pod {eid} initialization...", file=sys.stderr)
    start_time = time.time()
    
    while True:
        try:
            r = requests.get(f"{REST_URL}/endpoints/{eid}", headers=HEADERS)
            r.raise_for_status()
            data = r.json()
            
            workers = data.get('workers', [])
            active_states = ['IDLE', 'RUNNING']
            ready_workers = [w for w in workers if w.get('state') in active_states]
            
            if ready_workers:
                elapsed = int(time.time() - start_time)
                print(f"\n✅ Worker ready after {elapsed}s!", file=sys.stderr)
                return True
            
            initializing = [w for w in workers if w.get('state') == 'INITIALIZING']
            if initializing:
                print("   ... Still pulling image or loading weights ...", file=sys.stderr)
            else:
                print("   ... Waiting for worker to spin up ...", file=sys.stderr)
                
            time.sleep(20) # Poll every 20 seconds
        except Exception as e:
            print(f"⚠️  Status check failed: {e}. Retrying...", file=sys.stderr)
            time.sleep(5)

def down(eid):
    """Deletes the specified endpoint."""
    requests.delete(f"{REST_URL}/endpoints/{eid}", headers=HEADERS)
    print(f"🛑 Pod {eid} deleted.")

def get_cost():
    """Calculates approximate session cost."""
    # Simplified logic; can be expanded with RunPod pricing API
    return "$0.24 (Estimated)"

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "up": print(up())
    elif cmd == "down": down(sys.argv[2])
    elif cmd == "cost": print(get_cost())
    elif cmd == "wait": wait(sys.argv[2])