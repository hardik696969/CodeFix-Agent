# 🤖 CodeFix-Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

> An intelligent AI-powered agent that autonomously detects and fixes bugs in Python codebases using Large Language Models via Groq.

---

## 📌 Table of Contents
- [About](#about)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Future Scope](#future-scope)
- [Author](#author)

---

## 🧠 About

**CodeFix-Agent** is an autonomous software engineering agent that leverages the power of Large Language Models (LLMs) to automatically identify, analyze, and fix bugs in code. Built on top of the **mini-swe-agent** framework, it uses **Groq's ultra-fast LLM inference** to reason about code issues and apply intelligent fixes — all without human intervention.

This project is submitted as a **Final Year Project** in partial fulfillment of the requirements for the degree of Bachelor of Engineering in Computer Science.

---

## ✨ Features

- 🔍 **Automatic Bug Detection** — Identifies syntax, runtime, and logical errors
- 🛠️ **Autonomous Code Fixing** — Applies fixes without manual intervention
- ⚡ **Groq-Powered Inference** — Ultra-fast LLM responses using Groq API
- 🔁 **Iterative Fixing Loop** — Retries until tests pass
- 📄 **Detailed Logging** — Tracks agent decisions and actions
- 🧪 **Test-Driven Validation** — Validates fixes by running test suites
- 📦 **Modular Architecture** — Clean, extensible codebase

---

## 🏗️ Architecture

```
User Input (Buggy Code)
        ↓
  CodeFix-Agent
        ↓
  LLM via Groq API  ←→  Context Builder
        ↓
  Fix Generator
        ↓
  Test Runner / Validator
        ↓
  Fixed Code Output
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **Groq API** | LLM inference backend |
| **mini-swe-agent** | Base agent framework |
| **MkDocs** | Documentation |
| **pytest** | Testing framework |
| **pre-commit** | Code quality hooks |
| **pyproject.toml** | Project configuration |

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/hardik696969/CodeFix-Agent.git
cd CodeFix-Agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Set up Groq API Key
python setup_groq_env.py
```

---

## 🚀 Usage

```bash
# Run the agent on a buggy Python file
python -m minisweagent fix --file path/to/buggy_code.py

# Run with verbose logging
python -m minisweagent fix --file path/to/buggy_code.py --verbose
```

---

## 📁 Project Structure

```
CodeFix-Agent/
├── 📁 docs/                  # MkDocs documentation
├── 📁 src/
│   └── minisweagent/         # Core agent source code
├── 📁 tests/                 # Test suite
├── 📄 .gitignore
├── 📄 .pre-commit-config.yaml
├── 📄 mkdocs.yml             # Documentation config
├── 📄 pyproject.toml         # Project metadata
├── 📄 setup_groq_env.py      # Groq API setup script
└── 📄 README.md
```

---

## 🔮 Future Scope

- 🌐 Web UI using Streamlit for interactive demos
- 🐳 Docker containerization for easy deployment
- 📊 Evaluation benchmarks on real-world bug datasets
- 🔗 GitHub Integration — auto-fix issues via Pull Requests
- 🗂️ Multi-language support (JavaScript, Java, C++)
- 🧠 RAG on full codebases for better context understanding

---

## 👨‍💻 Author

**Hardik**
- GitHub: [@hardik696969](https://github.com/hardik696969)

---

## 📄 License

This project is licensed under the **MIT License**.

---

> ⭐ If you found this project helpful, please give it a star!