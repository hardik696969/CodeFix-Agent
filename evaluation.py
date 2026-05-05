import streamlit as st
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
from datetime import datetime

# Test Cases Dataset
TEST_CASES = [
    {
        "id": 1,
        "category": "ZeroDivisionError",
        "difficulty": "Easy",
        "buggy_code": """def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)""",
        "expected_fix": "add check for b == 0",
        "description": "Division by zero error"
    },
    {
        "id": 2,
        "category": "IndexError",
        "difficulty": "Easy",
        "buggy_code": """def get_first(lst):
    return lst[0]

print(get_first([]))""",
        "expected_fix": "add check for empty list",
        "description": "Index out of range on empty list"
    },
    {
        "id": 3,
        "category": "TypeError",
        "difficulty": "Easy",
        "buggy_code": """def add_numbers(a, b):
    return a + b

result = add_numbers("5", 10)
print(result)""",
        "expected_fix": "convert string to int",
        "description": "Adding string and integer"
    },
    {
        "id": 4,
        "category": "LogicError",
        "difficulty": "Medium",
        "buggy_code": """def is_palindrome(s):
    return s == s[::-0]

print(is_palindrome("racecar"))""",
        "expected_fix": "change -0 to -1",
        "description": "Wrong slice index in palindrome check"
    },
    {
        "id": 5,
        "category": "LogicError",
        "difficulty": "Medium",
        "buggy_code": """def factorial(n):
    if n == 0:
        return 0
    return n * factorial(n - 1)

print(factorial(5))""",
        "expected_fix": "base case should return 1 not 0",
        "description": "Wrong base case in factorial"
    },
    {
        "id": 6,
        "category": "KeyError",
        "difficulty": "Easy",
        "buggy_code": """def get_value(d, key):
    return d[key]

data = {"name": "Hardik"}
print(get_value(data, "age"))""",
        "expected_fix": "use dict.get() method",
        "description": "KeyError on missing dictionary key"
    },
    {
        "id": 7,
        "category": "InfiniteLoop",
        "difficulty": "Medium",
        "buggy_code": """def count_down(n):
    while n > 0:
        print(n)
        n + 1

count_down(5)""",
        "expected_fix": "change n + 1 to n -= 1",
        "description": "Infinite loop due to wrong operator"
    },
    {
        "id": 8,
        "category": "SyntaxError",
        "difficulty": "Easy",
        "buggy_code": """def greet(name)
    print("Hello, " + name)

greet("Hardik")""",
        "expected_fix": "add colon after function definition",
        "description": "Missing colon in function definition"
    },
    {
        "id": 9,
        "category": "AttributeError",
        "difficulty": "Medium",
        "buggy_code": """def reverse_string(s):
    return s.reverse()

print(reverse_string("hello"))""",
        "expected_fix": "use s[::-1] instead of s.reverse()",
        "description": "Wrong method used for string reversal"
    },
    {
        "id": 10,
        "category": "LogicError",
        "difficulty": "Hard",
        "buggy_code": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

print(bubble_sort([64, 34, 25, 12]))""",
        "expected_fix": "change range(n-i) to range(n-i-1)",
        "description": "Off-by-one error in bubble sort"
    }
]

def fix_code_with_groq(client, model, buggy_code, temperature=0.2):
    prompt = (
        "You are an expert Python debugging assistant.\n\n"
        "Analyze the following buggy Python code and fix ALL bugs in it.\n\n"
        "BUGGY CODE:\n"
        "```python\n"
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

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1024
    )
    return response.choices[0].message.content

def parse_fixed_code(output):
    if "FIXED_CODE:" in output and "```python" in output:
        code_start = output.find("```python", output.find("FIXED_CODE:")) + 9
        code_end = output.find("```", code_start)
        return output[code_start:code_end].strip()
    return None

def evaluate_fix(fixed_code, test_case):
    if fixed_code is None:
        return False
    try:
        exec(compile(fixed_code, "<string>", "exec"))
        return True
    except Exception:
        return False

# Streamlit UI
st.set_page_config(
    page_title="CodeFix Agent - Evaluation",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .eval-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="eval-title">📊 CodeFix Agent — Evaluation Module</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888;">Benchmark the agent across real-world bug scenarios</p>', unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.title("⚙️ Eval Settings")

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

    difficulty_filter = st.multiselect(
        "🎯 Difficulty Filter",
        ["Easy", "Medium", "Hard"],
        default=["Easy", "Medium", "Hard"]
    )

    st.divider()
    st.markdown("**📋 Test Suite Info**")
    st.info(f"Total Test Cases: **{len(TEST_CASES)}**")

# Filter test cases
filtered_tests = [t for t in TEST_CASES if t["difficulty"] in difficulty_filter]

# Overview
st.subheader("📋 Test Cases Overview")
df_overview = pd.DataFrame([{
    "ID": t["id"],
    "Category": t["category"],
    "Difficulty": t["difficulty"],
    "Description": t["description"]
} for t in filtered_tests])
st.dataframe(df_overview, use_container_width=True)

st.divider()

# Run Evaluation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_eval = st.button(
        "🚀 Run Full Evaluation",
        type="primary",
        use_container_width=True,
        disabled=not api_key
    )
    if not api_key:
        st.warning("⚠️ Enter your Groq API Key in the sidebar!")

if run_eval and api_key:
    client = Groq(api_key=api_key)

    results = []
    progress = st.progress(0, text="Starting evaluation...")
    status_container = st.empty()

    for i, test in enumerate(filtered_tests):
        status_container.info(f"🔄 Testing Case {test['id']}: {test['description']}...")

        start_time = time.time()
        success = False
        fixed_code = None
        error_msg = ""

        try:
            output = fix_code_with_groq(client, model, test["buggy_code"], temperature)
            fixed_code = parse_fixed_code(output)
            success = evaluate_fix(fixed_code, test)
            elapsed = round(time.time() - start_time, 2)
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            error_msg = str(e)

        results.append({
            "ID": test["id"],
            "Category": test["category"],
            "Difficulty": test["difficulty"],
            "Description": test["description"],
            "Status": "✅ Pass" if success else "❌ Fail",
            "Time (s)": elapsed,
            "Error": error_msg
        })

        progress.progress(
            (i + 1) / len(filtered_tests),
            text=f"Progress: {i+1}/{len(filtered_tests)} cases"
        )
        time.sleep(0.5)

    status_container.empty()
    progress.empty()

    # Results
    st.success("✅ Evaluation Complete!")
    df_results = pd.DataFrame(results)

    # Metrics
    total = len(results)
    passed = len([r for r in results if "Pass" in r["Status"]])
    failed = total - passed
    accuracy = round((passed / total) * 100, 1)
    avg_time = round(sum(r["Time (s)"] for r in results) / total, 2)

    st.subheader("📈 Results Summary")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Tests", total)
    m2.metric("✅ Passed", passed)
    m3.metric("❌ Failed", failed)
    m4.metric("🎯 Accuracy", f"{accuracy}%")
    m5.metric("⚡ Avg Time", f"{avg_time}s")

    st.divider()

    # Detailed Results
    st.subheader("📋 Detailed Results")
    st.dataframe(df_results, use_container_width=True)

    st.divider()

    # Charts
    st.subheader("📊 Analytics")

    chart1, chart2 = st.columns(2)

    with chart1:
        fig_pie = px.pie(
            values=[passed, failed],
            names=["Passed", "Failed"],
            title="Overall Pass/Fail Rate",
            color_discrete_sequence=["#00ff88", "#ff4444"]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart2:
        diff_stats = df_results.groupby("Difficulty").apply(
            lambda x: (x["Status"].str.contains("Pass").sum() / len(x)) * 100
        ).reset_index()
        diff_stats.columns = ["Difficulty", "Accuracy %"]

        fig_bar = px.bar(
            diff_stats,
            x="Difficulty",
            y="Accuracy %",
            title="Accuracy by Difficulty",
            color="Difficulty",
            color_discrete_map={
                "Easy": "#00ff88",
                "Medium": "#ffd200",
                "Hard": "#ff4444"
            }
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    fig_time = px.bar(
        df_results,
        x="ID",
        y="Time (s)",
        color="Status",
        title="Response Time per Test Case",
        color_discrete_map={
            "✅ Pass": "#00ff88",
            "❌ Fail": "#ff4444"
        }
    )
    st.plotly_chart(fig_time, use_container_width=True)

    cat_stats = df_results.groupby("Category").apply(
        lambda x: (x["Status"].str.contains("Pass").sum() / len(x)) * 100
    ).reset_index()
    cat_stats.columns = ["Category", "Accuracy %"]

    fig_cat = px.bar(
        cat_stats,
        x="Category",
        y="Accuracy %",
        title="Accuracy by Bug Category",
        color="Accuracy %",
        color_continuous_scale=["#ff4444", "#ffd200", "#00ff88"]
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # Export
    st.subheader("💾 Export Results")
    c1, c2 = st.columns(2)

    with c1:
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv,
            file_name=f"codefix_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c2:
        json_report = json.dumps({
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "accuracy": accuracy,
            "total": total,
            "passed": passed,
            "failed": failed,
            "avg_time": avg_time,
            "results": results
        }, indent=2)
        st.download_button(
            label="⬇️ Download JSON Report",
            data=json_report,
            file_name=f"codefix_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )