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

Edit `.env` and fill in your `RUNPOD_API_KEY` and `HF_TOKEN`.

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

1. **Backup**: Save your existing Claude Code settings from `~/.claude/settings.json`.
2. **Provision**: Check for existing pods or spin up a new one based on your `MODEL_ID`.
3. **Configure**: Automatically point Claude Code (CLI & VS Code) to the local proxy.
4. **Proxy**: Launch the LiteLLM proxy and wait for the model to load.
5. **Wait**: Provide a 10-second window to launch VS Code before the CLI starts.
6. **Launch**: Start `claude` code pre-configured for your RunPod backend.
7. **Cleanup**: Restore your original settings and offer to delete the Pod on exit.

### 🖥️ VS Code Integration

To use the proxy with the VS Code extension, you must launch VS Code from a **separate terminal tab** while the script is running:

1. Start `./start.sh` in Terminal Tab A.
2. Once the script says "Proxy is ready", open Terminal Tab B.
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