# Claude Code + Qwen3 RunPod Proxy

A high-performance, cost-effective backend for [Claude Code](https://claude.ai/code) using **Qwen3-Coder-Next** on RunPod Serverless.

## 🚀 Features
- **Auto-Provisioning**: Spins up a RunPod serverless GPU only when you need it.
- **Smart Discovery**: Checks for existing endpoints to avoid duplicate costs.
- **Claude Compatibility**: Uses LiteLLM to bridge the Anthropic tool-calling protocol to Qwen3.
- **Automatic Shutdown**: Prompts to tear down the infrastructure when you exit to save money.

## 🛠 Prerequisites
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Node.js](https://nodejs.org/) & `claude` CLI (`npm install -g @anthropic-ai/claude-code`)
- A RunPod account and API Key.

## 📦 Setup
1. **Clone & Configure**:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   cp .env.example .env


2. **Fill in `.env`**  Add your `RUNPOD_API_KEY`. You can find the `RUNPOD_TEMPLATE_ID` in your RunPod console (use the "RunPod vLLM" official template).

## 🏃 Usage

Run the unified launcher:

```bash
chmod +x start.sh
./start.sh

```

## 📄 License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---
