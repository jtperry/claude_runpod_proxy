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
import requests

API_KEY = os.getenv("RUNPOD_API_KEY")
TEMPLATE_ID = os.getenv("RUNPOD_TEMPLATE_ID")
# Use the new REST API base for management tasks
BASE_URL = "https://api.runpod.ai/v2/serverless/endpoint"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def get_existing_endpoints():
    """Returns a list of active endpoints named 'Claude-Code-Qwen3'."""
    # Note: Using GraphQL for list is often more reliable on RunPod for 'myself' queries
    query = """
    query Endpoints {
      myself {
        endpoints { id name templateId }
      }
    }
    """
    response = requests.post(
        "https://api.runpod.ai/graphql", 
        json={'query': query}, 
        headers=HEADERS
    )
    endpoints = response.json().get("data", {}).get("myself", {}).get("endpoints", [])
    return [e for e in endpoints if e['name'] == "Claude-Code-Qwen3"]

def create_endpoint():
    existing = get_existing_endpoints()
    
    if existing:
        print(f"🔎 Found {len(existing)} existing Claude-Code-Qwen3 endpoint(s).")
        for i, ep in enumerate(existing):
            print(f"  [{i}] ID: {ep['id']} (Template: {ep['templateId']})")
        
        choice = input("👉 Enter index to REUSE, or 'n' to create NEW: ").strip().lower()
        if choice != 'n':
            return existing[int(choice)]['id']

    print(f"📡 Creating fresh RunPod Serverless Endpoint...")
    payload = {
        "name": "Claude-Code-Qwen3",
        "templateId": TEMPLATE_ID,
        "gpuIds": "AMPERE_A100_40",
        "idleTimeout": 60,
        "workersMax": 1,
        "workersMin": 0
    }
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def delete_endpoint(endpoint_id):
    print(f"🛑 Tearing down endpoint {endpoint_id}...")
    url = f"{BASE_URL}/{endpoint_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 200:
        print("✅ Resources released.")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_pod.py [up|down] [id]")
        sys.exit(1)
    if sys.argv[1] == "up":
        print(create_endpoint())
    elif sys.argv[1] == "down":
        delete_endpoint(sys.argv[2])