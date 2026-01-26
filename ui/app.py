import streamlit as st
import requests

from theme import apply_dark_theme
from components import render_result
from charts import render_chart

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(
    page_title="Expense Intelligence System",
    layout="centered"
)

apply_dark_theme()

# ---------- Header ----------
st.markdown("## 💸 Expense Intelligence System")
st.markdown(
    "<p class='muted'>Ask questions about your expenses in plain English.</p>",
    unsafe_allow_html=True
)

# ---------- Examples ----------
with st.expander("💡 Example queries"):
    st.markdown("""
    - How much did I spend on food last month?
    - Show my Amazon purchases this month
    - Compare my spending this month vs last month
    - What is my biggest expense category?
    """)

# ---------- Input ----------
query = st.text_input(
    "Enter your query",
    placeholder="e.g. How much did I spend on food last month?"
)

if st.button("Analyze") and query:
    with st.spinner("Analyzing your expenses..."):
        res = requests.get(API_URL, params={"q": query})

    if res.status_code != 200:
        st.error("Backend API error. Is FastAPI running?")
    else:
        data = res.json()

        st.divider()
        render_result(data)