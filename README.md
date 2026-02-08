# Claude Code + RunPod Serverless Proxy

A high-performance, cost-effective backend for [Claude Code](https://claude.ai/code) using any Hugging Face model (Qwen3, DeepSeek, Llama) hosted on RunPod Serverless.

## 🚀 Features

* **Auto-Provisioning**: Spins up a RunPod serverless GPU only when you need it.
* **Smart Sizing**: Automatically recommends and selects the correct GPU (A100, H200, etc.) based on your selected model's VRAM requirements.
* **Template Discovery**: Automatically finds existing vLLM templates or creates a standard "vLLM-Worker" for you.
* **Pod Persistence**: Detects if you already have a pod running and offers to reuse it to save time and cold-start costs.
* **Cost Tracking**: Provides real-time session cost estimates based on official 2026 RunPod Flex rates.
* **Protocol Bridge**: Uses LiteLLM to translate Anthropic's tool-calling protocol to standard OpenAI/vLLM format.
* **Zero-Config Integration**: Automatically configures Claude Code's environment and settings for both CLI and VS Code during the session.
* **Seamless Restoration**: Backs up and restores your original Claude Code settings automatically when the session ends.
* **Local Backend Support**: Detects local LLM servers (Ollama, LM Studio) and offers to prioritize them over cloud GPUs.
* **Admin Console**: Includes a built-in LiteLLM UI for monitoring request logs and model performance.

## 📋 Prerequisites

* [uv](https://github.com/astral-sh/uv) (Fast Python package manager)
* [Node.js](https://nodejs.org/) & `claude` CLI (`npm install -g @anthropic-ai/claude-code`)
* A RunPod account and [API Key](https://www.google.com/search?q=https://www.runpod.io/console/user/settings).

## 🛠️ Setup

1. **Clone the repository**:

```bash
git clone <your-repo-url>
cd <your-repo-name>

```

2. **Configure Environment**:

```bash
cp .env.example .env

```

Edit `.env` and fill in your `RUNPOD_API_KEY`, `HF_TOKEN`, and optional `LOCAL_MODEL_ID` settings.

3. **Install Dependencies**:

```bash
uv sync

```

## 🏎️ Usage

Run the unified launcher script:

```bash
chmod +x start.sh
./start.sh

```

The script will:

1. **Local Check**: Probes for local Ollama or OpenAI-compatible servers and offers to use them.
2. **Provision**: Check for existing pods or spin up a new one on RunPod if local is skipped.
3. **Proxy**: Launch LiteLLM with Admin UI enabled at `http://0.0.0.0:4000/ui`.
4. **Wait**: Poll the RunPod API until the worker is warm (IDLE/RUNNING).
5. **Launch**: Start `claude` code pre-configured for the LiteLLM gateway.
6. **Cleanup**: Offer to delete the Pod on exit and restore local settings.

### 🖥️ VS Code Integration

To use the proxy with the VS Code extension, launch VS Code while the script is active:

1. Start `./start.sh` in Terminal Tab A.
2. Once the script says "Ready", open Terminal Tab B.
3. Run `code .` in Terminal Tab B.

## 🧠 GPU Estimation Logic

The tool automatically selects the GPU tier based on your `MODEL_ID`:

* **H200 (141GB)**: For DeepSeek-V3 / R1 Full weights.
* **A100 (80GB)**: For Qwen3-Coder-Next / 70B+ models.
* **RTX A6000 (48GB)**: For 32B models.
* **RTX 4090 (24GB)**: For 7B - 14B models.

## 📄 License

Copyright 2026 JT Perry

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)