import streamlit as st
import subprocess
import tempfile
import os
import time
from groq import Groq

# Page Config
st.set_page_config(
    page_title="CodeFix Agent - Feedback Loop",
    page_icon="🔁",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .loop-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FF416C, #FF4B2B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="loop-title">🔁 Feedback Loop Engine</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888;">Agent iteratively fixes code until all tests pass</p>', unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        placeholder="gsk_..."
    )

    model = st.selectbox(
        "🧠 Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama4-scout-17b-16e-instruct",
            "qwen-qwq-32b"
        ]
    )

    temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.2, 0.1)

    max_iterations = st.slider(
        "🔁 Max Iterations",
        min_value=1,
        max_value=10,
        value=5,
        help="Maximum number of fix attempts before giving up"
    )

    st.divider()
    st.markdown("""
    ### 💡 How It Works
    ```
    1. Agent fixes the code
    2. Code is executed
    3. If error → agent sees
       the error & retries
    4. Repeats until:
       ✅ Code passes, or
       ❌ Max attempts reached
    ```
    """)
    st.divider()
    st.markdown("Made with ❤️ by **Hardik**")

# Main Content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input")

    input_method = st.radio(
        "Input Method",
        ["✍️ Paste Code", "📁 Upload File"],
        horizontal=True
    )

    buggy_code = ""

    if input_method == "✍️ Paste Code":
        buggy_code = st.text_area(
            "Paste your buggy Python code:",
            height=250,
            placeholder="# Paste your buggy code here...",
            label_visibility="collapsed"
        )
    else:
        uploaded_file = st.file_uploader("Upload a Python file", type=["py"])
        if uploaded_file:
            buggy_code = uploaded_file.read().decode("utf-8")
            st.code(buggy_code, language="python")

    st.subheader("🧪 Test Cases")
    test_code = st.text_area(
        "Write test cases to validate the fix:",
        height=200,
        placeholder="""# Write your test cases here
# Example:
assert divide(10, 2) == 5, "Basic division failed"
assert divide(10, 0) == None, "Zero division should return None"
print("All tests passed!")""",
        label_visibility="collapsed"
    )

    error_desc = st.text_area(
        "📋 Describe the error (optional):",
        height=80,
        placeholder="e.g., Getting ZeroDivisionError..."
    )

    run_loop = st.button(
        "🚀 Start Feedback Loop!",
        type="primary",
        use_container_width=True,
        disabled=not api_key or not buggy_code
    )

    if not api_key:
        st.warning("⚠️ Enter your Groq API Key in the sidebar!")
    if not buggy_code:
        st.info("💡 Paste your buggy code to get started!")

with col2:
    st.subheader("🔁 Loop Progress")

    if run_loop and buggy_code and api_key:
        client = Groq(api_key=api_key)

        current_code = buggy_code
        all_attempts = []
        final_success = False
        start_total = time.time()

        loop_placeholder = st.empty()

        for iteration in range(1, max_iterations + 1):

            with loop_placeholder.container():
                st.markdown(f"### 🔄 Iteration {iteration} of {max_iterations}")
                st.progress(iteration / max_iterations)

            error_context = ""
            if all_attempts:
                last_attempt = all_attempts[-1]
                if not last_attempt["passed"]:
                    error_context = (
                        "Previous fix attempt failed with this error:\n"
                        + last_attempt["error"]
                        + "\n\nPlease fix this error too.\n\n"
                    )

            prompt = (
                "You are an expert Python debugging assistant.\n\n"
                "Analyze the following Python code and fix ALL bugs.\n\n"
                + error_context
                + (f"Error Description: {error_desc}\n\n" if error_desc else "")
                + "CODE TO FIX:\n"
                + "```python\n"
                + current_code
                + "\n```\n\n"
                + "Respond in this EXACT format:\n\n"
                + "FIXED_CODE:\n"
                + "```python\n"
                + "<your fixed code here>\n"
                + "```\n\n"
                + "EXPLANATION:\n"
                + "<what you fixed in this iteration>"
            )

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=2048
                )
                llm_output = response.choices[0].message.content

                fixed_code = None
                if "FIXED_CODE:" in llm_output and "```python" in llm_output:
                    code_start = llm_output.find("```python", llm_output.find("FIXED_CODE:")) + 9
                    code_end = llm_output.find("```", code_start)
                    fixed_code = llm_output[code_start:code_end].strip()

                explanation = ""
                if "EXPLANATION:" in llm_output:
                    exp_start = llm_output.find("EXPLANATION:") + 12
                    explanation = llm_output[exp_start:].strip()

                if not fixed_code:
                    all_attempts.append({
                        "iteration": iteration,
                        "code": current_code,
                        "passed": False,
                        "error": "Could not parse fixed code from LLM response",
                        "explanation": ""
                    })
                    continue

                full_code = fixed_code
                if test_code.strip():
                    full_code = fixed_code + "\n\n" + test_code

                exec_passed = False
                exec_error = ""

                try:
                    with tempfile.NamedTemporaryFile(
                        mode="w",
                        suffix=".py",
                        delete=False,
                        encoding="utf-8"
                    ) as f:
                        f.write(full_code)
                        temp_file = f.name

                    result = subprocess.run(
                        ["python", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    os.unlink(temp_file)

                    if result.returncode == 0:
                        exec_passed = True
                        exec_error = result.stdout
                    else:
                        exec_error = result.stderr

                except subprocess.TimeoutExpired:
                    exec_error = "TimeoutError: Code took too long to execute (possible infinite loop)"
                except Exception as e:
                    exec_error = str(e)

                all_attempts.append({
                    "iteration": iteration,
                    "code": fixed_code,
                    "passed": exec_passed,
                    "error": exec_error,
                    "explanation": explanation
                })

                if exec_passed:
                    final_success = True
                    current_code = fixed_code
                    break
                else:
                    current_code = fixed_code

            except Exception as e:
                all_attempts.append({
                    "iteration": iteration,
                    "code": current_code,
                    "passed": False,
                    "error": str(e),
                    "explanation": ""
                })

        loop_placeholder.empty()

        total_time = round(time.time() - start_total, 2)

        if final_success:
            st.success(f"✅ Code fixed successfully in {len(all_attempts)} iteration(s)!")
        else:
            st.error(f"❌ Could not fix code after {max_iterations} iterations!")

        m1, m2, m3 = st.columns(3)
        m1.metric("🔄 Iterations Used", len(all_attempts))
        m2.metric("⏱️ Total Time", f"{total_time}s")
        m3.metric("🎯 Result", "✅ Fixed" if final_success else "❌ Failed")

        st.divider()

        st.subheader("📜 Iteration History")
        for attempt in all_attempts:
            icon = "✅" if attempt["passed"] else "❌"

            with st.expander(f"{icon} Iteration {attempt['iteration']} — {'PASSED' if attempt['passed'] else 'FAILED'}"):
                st.markdown("**🔧 Fixed Code:**")
                st.code(attempt["code"], language="python")

                if attempt["explanation"]:
                    st.markdown("**📋 What was fixed:**")
                    st.markdown(attempt["explanation"])

                if attempt["error"]:
                    if attempt["passed"]:
                        st.markdown("**✅ Output:**")
                        st.code(attempt["error"])
                    else:
                        st.markdown("**❌ Error:**")
                        st.code(attempt["error"])

        if final_success:
            st.divider()
            st.subheader("🎉 Final Fixed Code")
            final_code = all_attempts[-1]["code"]
            st.code(final_code, language="python")

            st.download_button(
                label="⬇️ Download Final Fixed Code",
                data=final_code,
                file_name="final_fixed_code.py",
                mime="text/plain",
                use_container_width=True
            )

    else:
        st.markdown("""
        <div style='height:400px; border:2px dashed #333; border-radius:10px;
                    display:flex; align-items:center; justify-content:center;
                    flex-direction:column; color:#555;'>
            <h2>🔁</h2>
            <p>Feedback loop results will appear here</p>
            <p style='font-size:0.8rem;'>Enter code and click Start!</p>
        </div>
        """, unsafe_allow_html=True)