import streamlit as st
import difflib
from logger import CodeFixLogger

# Page Config
st.set_page_config(
    page_title="CodeFix Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #1a3a1a;
        border-left: 5px solid #00ff88;
        color: #00ff88;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #3a1a1a;
        border-left: 5px solid #ff4444;
        color: #ff4444;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #1a2a3a;
        border-left: 5px solid #00C9FF;
        color: #00C9FF;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">🤖 CodeFix Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Autonomous AI-Powered Bug Detection & Code Fixing using Groq LLM</p>', unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/robot.png", width=80)
    st.title("⚙️ Settings")

    st.subheader("🔑 Groq API Key")
    api_key = st.text_input(
        "Enter your Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your free API key from console.groq.com"
    )

    st.subheader("🧠 Model Selection")
    model = st.selectbox(
        "Choose LLM Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama4-scout-17b-16e-instruct",
            "qwen-qwq-32b"
        ]
    )

    st.subheader("🌡️ Temperature")
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.2, 0.1)

    st.subheader("🔁 Max Retries")
    max_retries = st.slider("Fix Attempts", 1, 5, 3)

    st.divider()
    st.markdown("**📊 Session Stats**")

    if "total_fixes" not in st.session_state:
        st.session_state.total_fixes = 0
    if "success_count" not in st.session_state:
        st.session_state.success_count = 0

    col1, col2 = st.columns(2)
    col1.metric("Total Runs", st.session_state.total_fixes)
    col2.metric("Successful", st.session_state.success_count)

    st.divider()
    st.markdown("Made with ❤️ by **Hardik**")
    st.markdown("[GitHub](https://github.com/hardik696969/CodeFix-Agent)")

# Tabs
tab1, tab2, tab3 = st.tabs(["🛠️ Fix Code", "📊 Diff Viewer", "📖 How It Works"])

# TAB 1
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Input — Buggy Code")

        input_method = st.radio(
            "Input Method",
            ["✍️ Paste Code", "📁 Upload File"],
            horizontal=True
        )

        buggy_code = ""

        if input_method == "✍️ Paste Code":
            buggy_code = st.text_area(
                "Paste your buggy Python code here:",
                height=350,
                placeholder="# Paste your buggy Python code here...",
                label_visibility="collapsed"
            )
        else:
            uploaded_file = st.file_uploader("Upload a Python file", type=["py"])
            if uploaded_file:
                buggy_code = uploaded_file.read().decode("utf-8")
                st.code(buggy_code, language="python")

        error_desc = st.text_area(
            "📋 Describe the error (optional):",
            height=100,
            placeholder="e.g., Getting ZeroDivisionError when list is empty..."
        )

        fix_clicked = st.button(
            "🚀 Fix My Code!",
            type="primary",
            use_container_width=True,
            disabled=not api_key or not buggy_code
        )

        if not api_key:
            st.markdown('<div class="error-box">⚠️ Please enter your Groq API Key in the sidebar!</div>', unsafe_allow_html=True)
        if not buggy_code:
            st.markdown('<div class="info-box">💡 Paste your buggy code or upload a file to get started!</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("✅ Output — Fixed Code")

        if fix_clicked and buggy_code and api_key:
            with st.spinner("🤖 Agent is analyzing and fixing your code..."):
                try:
                    from groq import Groq

                    client = Groq(api_key=api_key)

                    error_part = "Error Description: " + error_desc + "\n\n" if error_desc else ""

                    prompt = (
                        "You are an expert Python debugging assistant.\n\n"
                        "Analyze the following buggy Python code and fix ALL bugs in it.\n\n"
                        + error_part
                        + "BUGGY CODE:\n"
                        + "```python\n"
                        + buggy_code
                        + "\n```\n\n"
                        + "Respond in this EXACT format:\n\n"
                        + "FIXED_CODE:\n"
                        + "```python\n"
                        + "<your fixed code here>\n"
                        + "```\n\n"
                        + "EXPLANATION:\n"
                        + "<bullet points explaining what bugs were found and fixed>\n\n"
                        + "BUGS_FOUND:\n"
                        + "<number of bugs fixed>"
                    )

                    fixed_output = ""
                    attempts = 0
                    success = False

                    progress_bar = st.progress(0, text="Starting fix attempt...")

                    for attempt in range(max_retries):
                        attempts += 1
                        progress_bar.progress(
                            (attempt + 1) / max_retries,
                            text=f"🔄 Attempt {attempt + 1} of {max_retries}..."
                        )

                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperature,
                            max_tokens=2048
                        )

                        fixed_output = response.choices[0].message.content

                        if "FIXED_CODE:" in fixed_output and "```python" in fixed_output:
                            success = True
                            break

                    progress_bar.empty()

                    if success:
                        code_start = fixed_output.find("```python", fixed_output.find("FIXED_CODE:")) + 9
                        code_end = fixed_output.find("```", code_start)
                        fixed_code = fixed_output[code_start:code_end].strip()

                        explanation = ""
                        if "EXPLANATION:" in fixed_output:
                            exp_start = fixed_output.find("EXPLANATION:") + 12
                            exp_end = fixed_output.find("BUGS_FOUND:") if "BUGS_FOUND:" in fixed_output else len(fixed_output)
                            explanation = fixed_output[exp_start:exp_end].strip()

                        bugs_count = "N/A"
                        if "BUGS_FOUND:" in fixed_output:
                            bugs_start = fixed_output.find("BUGS_FOUND:") + 11
                            bugs_count = fixed_output[bugs_start:].strip().split("\n")[0].strip()

                        logger = CodeFixLogger(model=model)
                        logger.log_attempt(
                            buggy_code=buggy_code,
                            fixed_code=fixed_code,
                            success=True,
                            error="",
                            explanation=explanation,
                            iteration=attempts,
                            elapsed_time=0.0,
                            category="user_input"
                        )

                        st.session_state.buggy_code = buggy_code
                        st.session_state.fixed_code = fixed_code
                        st.session_state.total_fixes += 1
                        st.session_state.success_count += 1

                        st.code(fixed_code, language="python")

                        m1, m2, m3 = st.columns(3)
                        m1.metric("🐛 Bugs Fixed", bugs_count)
                        m2.metric("🔄 Attempts", attempts)
                        m3.metric("🧠 Model", model.split("-")[0].upper())

                        st.subheader("📋 Explanation")
                        st.markdown(explanation)

                        st.download_button(
                            label="⬇️ Download Fixed Code",
                            data=fixed_code,
                            file_name="fixed_code.py",
                            mime="text/plain",
                            use_container_width=True
                        )

                        st.markdown('<div class="success-box">✅ Code fixed successfully!</div>', unsafe_allow_html=True)

                    else:
                        st.session_state.total_fixes += 1
                        st.markdown('<div class="error-box">❌ Agent could not fix the code after maximum retries.</div>', unsafe_allow_html=True)

                except ImportError:
                    st.error("❌ Groq package not installed! Run: pip install groq")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        else:
            st.markdown("""
            <div style='height:350px; border:2px dashed #333; border-radius:10px;
                        display:flex; align-items:center; justify-content:center;
                        flex-direction:column; color:#555;'>
                <h2>🤖</h2>
                <p>Fixed code will appear here</p>
            </div>
            """, unsafe_allow_html=True)

# TAB 2
with tab2:
    st.subheader("📊 Code Diff Viewer")

    if "buggy_code" in st.session_state and "fixed_code" in st.session_state:
        diff = difflib.unified_diff(
            st.session_state.buggy_code.splitlines(keepends=True),
            st.session_state.fixed_code.splitlines(keepends=True),
            fromfile="buggy_code.py",
            tofile="fixed_code.py",
            lineterm=""
        )
        diff_text = "\n".join(list(diff))

        if diff_text:
            st.code(diff_text, language="diff")
        else:
            st.info("No differences found!")

        st.subheader("👁️ Side-by-Side View")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**❌ Before (Buggy)**")
            st.code(st.session_state.buggy_code, language="python")
        with c2:
            st.markdown("**✅ After (Fixed)**")
            st.code(st.session_state.fixed_code, language="python")
    else:
        st.markdown('<div class="info-box">💡 Fix some code in the <strong>Fix Code</strong> tab first!</div>', unsafe_allow_html=True)

# TAB 3
with tab3:
    st.subheader("📖 How CodeFix Agent Works")
    st.markdown("""
    ### 🔄 Agent Pipeline
    ```
    1️⃣  User inputs buggy Python code
            ↓
    2️⃣  CodeFix Agent builds a structured prompt
            ↓
    3️⃣  Groq LLM analyzes the code
            ↓
    4️⃣  Agent extracts the fixed code
            ↓
    5️⃣  Validation & retry loop (up to N times)
            ↓
    6️⃣  Fixed code + explanation returned to user
    ```
    ---
    ### 🧠 Models Available
    | Model | Speed | Quality | Best For |
    |-------|-------|---------|----------|
    | LLaMA 3.3 70B | ⚡⚡ | ⭐⭐⭐⭐⭐ | Complex bugs |
    | LLaMA 3.1 8B | ⚡⚡⚡ | ⭐⭐⭐⭐ | Simple fixes |
    | LLaMA4 Scout 17B | ⚡⚡ | ⭐⭐⭐⭐⭐ | Mixed tasks |
    | Qwen QwQ 32B | ⚡⚡⚡ | ⭐⭐⭐⭐ | Quick fixes |
    ---
    ### 🐛 Types of Bugs Fixed
    - **Syntax Errors** — Missing colons, brackets, indentation
    - **Runtime Errors** — ZeroDivisionError, IndexError, KeyError
    - **Logical Errors** — Wrong conditions, off-by-one errors
    - **Type Errors** — Wrong data types, incorrect casting
    - **Name Errors** — Undefined variables, wrong function names
    """)