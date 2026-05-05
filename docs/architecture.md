# 🏗️ Architecture

## System Overview
┌─────────────────────────────────────────────────────┐
│ CodeFix Agent │
├─────────────────────────────────────────────────────┤
│ │
│ User Input (Buggy Code) │
│ ↓ │
│ Prompt Builder │
│ ↓ │
│ Groq LLM API ←──────────────────────────────┐ │
│ ↓ │ │
│ Response Parser │ │
│ ↓ │ │
│ Code Executor & Validator │ │
│ ↓ │ │
│ Tests Pass? ──── NO ──── Error Feedback ──────┘ │
│ │ │
│ YES │
│ ↓ │
│ Fixed Code Output + Explanation │
│ ↓ │
│ Logger → Log Dashboard │
│ │
└─────────────────────────────────────────────────────┘

---

## Components

### 1. Web UI (`app.py`)
- Built with **Streamlit**
- Handles user input and displays output
- Integrates with Logger

### 2. Evaluation Module (`evaluation.py`)
- 10 pre-defined test cases
- Easy / Medium / Hard difficulty
- Generates performance reports

### 3. Feedback Loop (`feedback_loop.py`)
- Iterative fix attempts
- Real code execution
- Error fed back to LLM

### 4. Logger (`logger.py`)
- Session-based logging
- JSON storage
- Master log aggregation

### 5. Log Dashboard (`log_dashboard.py`)
- Real-time analytics
- Charts & visualizations
- Export capabilities

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| LLM Backend | Groq API |
| Agent Framework | mini-swe-agent |
| Logging | JSON + Python |
| Visualization | Plotly |
| Containerization | Docker |
| Documentation | MkDocs Material |

---

## Data Flow
User
│
▼
Streamlit UI (app.py)
│
▼
Prompt Builder
│
▼
Groq API (LLM)
│
▼
Response Parser
│
├──► Fixed Code ──► Code Executor
│ │
│ Pass/Fail?
│ │
│ ┌────Pass─┴─Fail────┐
│ ▼ ▼
│ Return Fix Feedback Loop
│ │ │
│ └────────┬──────────┘
│ ▼
└──────────────► Logger & Dashboard
