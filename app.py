import streamlit as st
import pandas as pd
import numpy as np
from gpt_helper import generate_code_for_query
from code_executor import safe_execute
from utils import extract_schema, render_result
from PIL import Image

st.set_page_config(page_title="AI Data Analytics Copilot", layout='wide')
try:
    logo = Image.open("logo.png")
    st.image(logo, width=90)
except Exception:
    st.markdown("### 🤖 AI Data Analytics Copilot")

st.markdown(
    "<h4 style='color:#1E88E5;'>Ask questions to your data in plain English — get instant visual answers ⚡</h4>",
    unsafe_allow_html=True
)
st.markdown("---")

st.sidebar.header("📁 Upload & Settings")
uploaded = st.sidebar.file_uploader("Upload CSV or Excel", type=['csv','xlsx','xls'])
model_choice = st.sidebar.selectbox("Choose Model", ["gpt-4-turbo", "gpt-3.5-turbo"], index=0)
st.sidebar.info("Add your OpenAI API key as an environment variable before running.")

if uploaded is None:
    st.info("No file uploaded — using sample_data.csv included with the project.")
    df = pd.read_csv("sample_data.csv")
else:
    try:
        if uploaded.type.startswith("text") or uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

col1, col2 = st.columns([1.2, 2.5])

with col1:
    st.subheader("💬 Ask your question")
    query = st.text_area("Example: Show total revenue by month", height=100)
    run = st.button("🚀 Analyze")

    with st.expander("📄 Dataset Preview", expanded=True):
        st.dataframe(df.head(10))

    st.sidebar.subheader("📊 Dataset Schema")
    schema = extract_schema(df)
    st.sidebar.write(schema)

with col2:
    if run and query.strip():
        with st.spinner("🤖 Generating code with GPT..."):
            code = generate_code_for_query(query, {"columns": schema, "n_rows": len(df)}, model=model_choice)

        st.subheader("🧠 Generated pandas code")
        st.code(code, language="python")

        with st.spinner("⚙️ Executing code..."):
            result, logs = safe_execute(code, df.copy())

        if result is not None:
            st.success("✅ Done! Here's your result:")
            render_result(result)

        if logs:
            with st.expander("🪵 Execution Logs"):
                st.text(logs)

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px;'>"
    "🚀 Built by <b>Sanketh BSR</b> | Powered by OpenAI GPT & Streamlit</div>",
    unsafe_allow_html=True
)
