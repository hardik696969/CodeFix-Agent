import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="CodeFix Agent - Logs",
    page_icon="📝",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .log-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #834d9b, #d04ed6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="log-title">📝 CodeFix Agent — Log Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888;">Real-time analytics and logs of all agent activities</p>', unsafe_allow_html=True)
st.divider()

# Load Logs
LOG_DIR = Path("logs")
MASTER_LOG_FILE = LOG_DIR / "master_log.json"

def load_logs():
    if not MASTER_LOG_FILE.exists():
        return []
    with open(MASTER_LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return []

# Sidebar
with st.sidebar:
    st.title("⚙️ Filters")

    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()

    st.divider()
    st.markdown("**📁 Log Files**")

    if LOG_DIR.exists():
        log_files = list(LOG_DIR.glob("session_*.json"))
        st.info(f"Total Sessions: **{len(log_files)}**")
        for f in log_files[-5:]:
            st.markdown(f"📄 `{f.name}`")
    else:
        st.warning("No logs found yet!")

    st.divider()
    st.markdown("Made with ❤️ by **Hardik**")

# Load data
all_sessions = load_logs()

if not all_sessions:
    st.markdown("""
    <div style='height:300px; border:2px dashed #333; border-radius:10px;
                display:flex; align-items:center; justify-content:center;
                flex-direction:column; color:#555;'>
        <h2>📝</h2>
        <p>No logs found yet!</p>
        <p style='font-size:0.8rem;'>Run the agent first to generate logs</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Flatten all logs
all_logs = []
for session in all_sessions:
    for log in session.get("logs", []):
        log["session_id"] = session["session_id"]
        log["model"] = session["model"]
        all_logs.append(log)

if not all_logs:
    st.warning("No log entries found!")
    st.stop()

df = pd.DataFrame(all_logs)

# ─── Overview Metrics ────────────────────────────────────────────
st.subheader("📊 Overall Metrics")

total = len(df)
passed = df["success"].sum()
failed = total - passed
accuracy = round((passed / total) * 100, 1) if total > 0 else 0
avg_time = round(df["elapsed_time"].mean(), 2) if "elapsed_time" in df.columns else 0
total_sessions = len(all_sessions)

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("📋 Total Logs", total)
m2.metric("🖥️ Sessions", total_sessions)
m3.metric("✅ Passed", int(passed))
m4.metric("❌ Failed", int(failed))
m5.metric("🎯 Accuracy", f"{accuracy}%")
m6.metric("⚡ Avg Time", f"{avg_time}s")

st.divider()

# ─── Charts ──────────────────────────────────────────────────────
st.subheader("📈 Analytics")

chart1, chart2 = st.columns(2)

with chart1:
    fig_pie = px.pie(
        values=[int(passed), int(failed)],
        names=["Passed", "Failed"],
        title="Overall Pass/Fail Rate",
        color_discrete_sequence=["#00ff88", "#ff4444"]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with chart2:
    if "category" in df.columns:
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_cat = px.bar(
            cat_counts,
            x="Category",
            y="Count",
            title="Logs by Bug Category",
            color="Count",
            color_continuous_scale=["#834d9b", "#d04ed6"]
        )
        st.plotly_chart(fig_cat, use_container_width=True)

# Success over time
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_sorted = df.sort_values("timestamp")
    df_sorted["cumulative_success"] = df_sorted["success"].cumsum()

    fig_time = px.line(
        df_sorted,
        x="timestamp",
        y="cumulative_success",
        title="Cumulative Successful Fixes Over Time",
        color_discrete_sequence=["#00C9FF"]
    )
    st.plotly_chart(fig_time, use_container_width=True)

# Time per attempt
if "elapsed_time" in df.columns:
    fig_elapsed = px.histogram(
        df,
        x="elapsed_time",
        nbins=20,
        title="Response Time Distribution",
        color_discrete_sequence=["#834d9b"]
    )
    st.plotly_chart(fig_elapsed, use_container_width=True)

st.divider()

# ─── Session Explorer ────────────────────────────────────────────
st.subheader("🖥️ Session Explorer")

for session in all_sessions:
    session_logs = session.get("logs", [])
    total_s = len(session_logs)
    passed_s = sum(1 for l in session_logs if l.get("success"))
    acc_s = round((passed_s / total_s) * 100, 1) if total_s > 0 else 0

    with st.expander(f"📁 Session {session['session_id']} | Model: {session['model']} | Accuracy: {acc_s}%"):
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total", total_s)
        s2.metric("✅ Passed", passed_s)
        s3.metric("❌ Failed", total_s - passed_s)
        s4.metric("🎯 Accuracy", f"{acc_s}%")

        if session_logs:
            df_session = pd.DataFrame(session_logs)
            cols_to_show = ["id", "timestamp", "category", "iteration", "elapsed_time", "success"]
            cols_available = [c for c in cols_to_show if c in df_session.columns]
            st.dataframe(df_session[cols_available], use_container_width=True)

st.divider()

# ─── Raw Log Viewer ──────────────────────────────────────────────
st.subheader("🔍 Raw Log Viewer")

cols_to_show = ["id", "session_id", "timestamp", "model", "category", "iteration", "elapsed_time", "success"]
cols_available = [c for c in cols_to_show if c in df.columns]
st.dataframe(df[cols_available], use_container_width=True)

st.divider()

# ─── Export ──────────────────────────────────────────────────────
st.subheader("💾 Export Logs")

c1, c2 = st.columns(2)

with c1:
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"codefix_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with c2:
    with open(MASTER_LOG_FILE, "r") as f:
        raw_json = f.read()
    st.download_button(
        label="⬇️ Download JSON",
        data=raw_json,
        file_name=f"codefix_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )