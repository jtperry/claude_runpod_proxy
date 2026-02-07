# Claude Code + RunPod Serverless Proxy

A high-performance, cost-effective backend for [Claude Code](https://claude.ai/code) using any Hugging Face model (Qwen3, DeepSeek, Llama) hosted on RunPod Serverless.

## 🚀 Features

* **Auto-Provisioning**: Spins up a RunPod serverless GPU only when you need it.
* **Smart Sizing**: Automatically recommends and selects the correct GPU (A100, H200, etc.) based on your selected model's VRAM requirements.
* **Template Discovery**: Automatically finds existing vLLM templates or creates a standard "vLLM-Worker" for you.
* **Pod Persistence**: Detects if you already have a pod running and offers to reuse it to save time and cold-start costs.
* **Cost Tracking**: Provides real-time session cost estimates based on official 2026 RunPod Flex rates.
* **Protocol Bridge**: Uses LiteLLM to translate Anthropic's tool-calling protocol to standard OpenAI/vLLM format.

## 🛠 Prerequisites

* [uv](https://github.com/astral-sh/uv) (Fast Python package manager)
* [Node.js](https://nodejs.org/) & `claude` CLI (`npm install -g @anthropic-ai/claude-code`)
* A RunPod account and [API Key](https://www.google.com/search?q=https://www.runpod.io/console/user/settings).

## 📦 Setup

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd <your-repo-name>

```


2. **Configure Environment**:
```bash
cp .env.example .env

```


Edit `.env` and fill in your `RUNPOD_API_KEY` and `HF_TOKEN`.
3. **Install Dependencies**:
```bash
uv sync

```



## 🏃 Usage

Run the unified launcher script:

```bash
chmod +x start.sh
./start.sh

```

The script will:

1. Validate your model on Hugging Face.
2. Quote you an hourly price.
3. Check for existing pods or spin up a new one.
4. Launch the LiteLLM proxy.
5. Launch `claude` code, pre-configured to use your RunPod backend.

## 💰 GPU Estimation Logic

The tool automatically selects the GPU tier based on your `MODEL_ID`:

* **H200 (141GB)**: For DeepSeek-V3 / R1 Full weights.
* **A100 (80GB)**: For Qwen3-Coder-Next / 70B+ models.
* **RTX A6000 (48GB)**: For 32B models.
* **RTX 4090 (24GB)**: For 7B - 14B models.

## 📄 License

Copyright 2026 JT Perry

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.