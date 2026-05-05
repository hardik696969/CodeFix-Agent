# 🌐 Web UI Module

## Overview
The Web UI is built using **Streamlit** and provides an intuitive 
interface for users to interact with CodeFix Agent.

---

## Features

| Feature | Description |
|---------|-------------|
| ✍️ Code Input | Paste code directly in text area |
| 📁 File Upload | Upload `.py` files directly |
| 🧠 Model Selection | Choose from 4 Groq LLM models |
| 🌡️ Temperature Control | Adjust creativity level |
| 🔁 Retry Control | Set max fix attempts |
| 📊 Diff Viewer | Side-by-side before/after comparison |
| ⬇️ Download | Download fixed code as `.py` file |
| 📈 Session Stats | Track total runs and successes |

---

## How to Use

### Step 1: Enter API Key
- Open the sidebar
- Enter your **Groq API Key**

### Step 2: Input Code
- Paste your buggy code **or** upload a `.py` file
- Optionally describe the error

### Step 3: Fix Code
- Click **🚀 Fix My Code!**
- Watch the progress bar
- Get your fixed code!

### Step 4: View Diff
- Go to **📊 Diff Viewer** tab
- See exactly what changed

---

## Usage
```bash
streamlit run app.py