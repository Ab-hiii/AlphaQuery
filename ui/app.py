import streamlit as st
import requests

from theme import apply_dark_theme
from components import render_result
from charts import render_chart

# ------------------------------------------------------------------
# Page configuration (NEW)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AlphaQuery",
    page_icon="🧠",
    layout="wide"
)

# ------------------------------------------------------------------
# Navigation (NEW)
# ------------------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    options=["🏠 Query Interface", "🧪 Test Runner", "📊 Dashboard"],
    index=0
)

API_URL = "http://127.0.0.1:8000/query"

# ------------------------------------------------------------------
# QUERY INTERFACE (Existing app, unchanged)
# ------------------------------------------------------------------
if page == "🏠 Query Interface":

    apply_dark_theme()

    # ---------- Header ----------
    st.markdown("## 🧠 AlphaQuery")
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

# ------------------------------------------------------------------
# TEST RUNNER PAGE (NEW)
# ------------------------------------------------------------------
elif page == "🧪 Test Runner":
    import sys
    sys.path.append("ui/pages")

    try:
        from test_runner import main as test_runner_main
        test_runner_main()
    except Exception as e:
        st.error("Failed to load Test Runner")
        st.exception(e)

# ------------------------------------------------------------------
# DASHBOARD PAGE (Placeholder)
# ------------------------------------------------------------------
elif page == "📊 Dashboard":
    st.info("📊 Dashboard coming soon!")