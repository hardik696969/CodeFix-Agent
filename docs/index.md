# 🤖 CodeFix Agent

> **Autonomous AI-Powered Bug Detection & Code Fixing using Groq LLM**

---

## 🎯 What is CodeFix Agent?

CodeFix Agent is an intelligent autonomous software engineering agent that leverages 
the power of Large Language Models (LLMs) to automatically identify, analyze, and fix 
bugs in Python code — without any human intervention.

Built on top of the **mini-swe-agent** framework and powered by **Groq's ultra-fast 
LLM inference**, CodeFix Agent represents the next generation of AI-assisted 
software development tools.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Auto Bug Detection** | Identifies syntax, runtime & logical errors |
| 🛠️ **Autonomous Fixing** | Applies fixes without manual intervention |
| ⚡ **Groq-Powered** | Ultra-fast LLM inference via Groq API |
| 🔁 **Feedback Loop** | Iteratively retries until tests pass |
| 📊 **Evaluation Module** | Benchmarks agent performance |
| 📝 **Logging System** | Tracks all agent decisions & actions |
| 🌐 **Web UI** | Beautiful Streamlit interface |
| 🐳 **Docker Ready** | One-command deployment |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/hardik696969/CodeFix-Agent.git
cd CodeFix-Agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py