# Copyright 2026 JT Perry
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except 
# in compliance with the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import os, sys, requests, time

# Configuration from .env
API_KEY = os.getenv("RUNPOD_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# 2026 REST Management URL
REST_URL = "https://rest.runpod.io/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
COST_FILE = ".pod_info"

# Exact Enum strings required by RunPod REST API for provisioning
GPU_CONFIGS = {
    "SMALL":  {"id": "NVIDIA GeForce RTX 4090", "name": "RTX 4090 (24GB)", "rate": 0.00031},
    "MEDIUM": {"id": "NVIDIA RTX A6000", "name": "RTX A6000 (48GB)", "rate": 0.00034},
    "LARGE":  {"id": "NVIDIA A100 80GB PCIe", "name": "A100 (80GB)", "rate": 0.00076},
    "XLARGE": {"id": "NVIDIA H200", "name": "H200 (141GB)", "rate": 0.00155}
}

def get_or_create_template():
    """Finds or creates a vLLM template with optimized defaults for coding tasks."""
    try:
        r = requests.get(f"{REST_URL}/templates", headers=HEADERS)
        r.raise_for_status()
        
        # Unique template name per model to avoid environment collisions
        template_name = f"vLLM-{MODEL_ID.split('/')[-1]}"
        for t in r.json():
            if t['name'] == template_name and t.get('isServerless'):
                return t['id']

        print(f"🛠️  Creating template '{template_name}'...", file=sys.stderr)
        payload = {
            "name": template_name,
            "imageName": "runpod/worker-v1-vllm:latest",
            "isServerless": True,
            "containerDiskInGb": 50,
            "env": {
                "MODEL_NAME": MODEL_ID, 
                "HF_TOKEN": HF_TOKEN,
                "MAX_MODEL_LEN": "32768",          # High context for code analysis
                "GPU_MEMORY_UTILIZATION": "0.90",  # Default safety buffer for overhead
                "DTYPE": "auto"                    # Standard for mixed precision weights
            }
        }
        resp = requests.post(f"{REST_URL}/templates", json=payload, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()["id"]
    except Exception as e:
        print(f"❌ Template Error: {e}", file=sys.stderr)
        sys.exit(1)

def get_existing_pod():
    """Checks for active endpoints named 'Claude-Auto-Pod'."""
    try:
        r = requests.get(f"{REST_URL}/endpoints", headers=HEADERS)
        if r.status_code == 200:
            return [e for e in r.json() if e.get('name') == "Claude-Auto-Pod"]
    except: return []
    return []

def up():
    # 1. Check for existing pods to reuse
    existing = get_existing_pod()
    if existing:
        print(f"🔎 Found active pod: {existing[0]['id']}", file=sys.stderr)
        sys.stderr.write("👉 Use existing pod? (y/n): ")
        sys.stderr.flush()
        if sys.stdin.readline().strip().lower() == 'y':
            return existing[0]['id']

    # 2. Automatic GPU Selection Logic
    m = MODEL_ID.lower()
    gpu = GPU_CONFIGS["XLARGE"] if any(x in m for x in ["deepseek-v3", "deepseek-r1"]) and "distill" not in m else \
          GPU_CONFIGS["LARGE"]  if any(x in m for x in ["qwen3-coder-next", "70b", "80b"]) else \
          GPU_CONFIGS["MEDIUM"] if "32b" in m else GPU_CONFIGS["SMALL"]

    print(f"\n🤖 Model: {MODEL_ID}\n🖥️  GPU:   {gpu['name']}\n💰 Rate:  ${gpu['rate']*3600:.2f}/hr\n", file=sys.stderr)
    
    sys.stderr.write("🚀 Launch new pod? (y/n): ")
    sys.stderr.flush()
    if sys.stdin.readline().strip().lower() != 'y':
        print("Aborted.", file=sys.stderr)
        sys.exit(0)

    # 3. Create Endpoint with strictly compliant REST schema
    tid = get_or_create_template()
    payload = {
        "name": "Claude-Auto-Pod",
        "templateId": tid,
        "gpuTypeIds": [gpu['id']],
        "idleTimeout": 120,    # Warm for 2 mins between prompts
        "workersMax": 1,       # Stay within account worker quota
        "workersMin": 0        # Scale to zero when inactive
    }
    
    r = requests.post(f"{REST_URL}/endpoints", json=payload, headers=HEADERS)
    if r.status_code != 200:
        print(f"💥 Provisioning Failed ({r.status_code}): {r.text}", file=sys.stderr)
        sys.exit(1)
        
    eid = r.json()["id"]
    with open(COST_FILE, "w") as f: f.write(f"{eid},{time.time()},{gpu['rate']}")
    return eid

def get_cost():
    """Calculates estimated cost since script started."""
    if not os.path.exists(COST_FILE): return "$0.00"
    with open(COST_FILE, "r") as f:
        data = f.read().split(",")
        if len(data) < 3: return "$0.00"
        _, start_time, rate = data
    elapsed = time.time() - float(start_time)
    return f"${(elapsed * float(rate)):.4f}"

def down(eid):
    """Deletes the serverless endpoint via REST API."""
    print(f"💰 Final Session Cost: {get_cost()}", file=sys.stderr)
    requests.delete(f"{REST_URL}/endpoints/{eid}", headers=HEADERS)
    if os.path.exists(COST_FILE): os.remove(COST_FILE)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    if sys.argv[1] == "up": print(up())
    elif sys.argv[1] == "down": down(sys.argv[2])
    elif sys.argv[1] == "cost": print(get_cost())