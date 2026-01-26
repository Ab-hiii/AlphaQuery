import sys
from pathlib import Path

# -------------------------------------------------
# Ensure project root is on PYTHONPATH (Streamlit Cloud fix)
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from datetime import datetime

# -------------------- Core NLP imports --------------------
from core.intent_matcher import IntentMatcher
from core.entity_extractor import EntityExtractor
from core.date_parser import DateParser
from core.executor import Executor

# -------------------- UI helpers --------------------
from ui.charts import render_chart

# -------------------- Page config --------------------
st.set_page_config(
    page_title="AlphaQuery · Expense NLP System",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------- Initialize NLP pipeline (once) --------------------
@st.cache_resource
def load_pipeline():
    return (
        IntentMatcher(),
        EntityExtractor(),
        DateParser(),
        Executor()
    )

intent_matcher, entity_extractor, date_parser, executor = load_pipeline()

# -------------------- Header --------------------
st.markdown(
    """
    <h1 style="text-align:center;">💸 AlphaQuery</h1>
    <p style="text-align:center; color:#9aa0a6;">
    Ask questions about your expenses in plain English
    </p>
    """,
    unsafe_allow_html=True
)

# -------------------- Example queries --------------------
with st.expander("💡 Example queries"):
    st.markdown(
        """
        - How much did I spend on food last month?
        - Show my Uber rides this month
        - What is my biggest expense category?
        - Compare my food expenses in June and July
        - List expenses above 1000 this month
        """
    )

# -------------------- Query input --------------------
query = st.text_input(
    "Enter your query",
    placeholder="e.g. What is my biggest expense category?"
)

run = st.button("Analyze")

# -------------------- Run pipeline --------------------
if run and query.strip():
    with st.spinner("Analyzing your query..."):
        intent = intent_matcher.match_intent(query)
        entities = entity_extractor.extract(query)
        start_date, end_date = date_parser.parse(query)
        result = executor.execute(
            intent["intent"],
            entities,
            start_date,
            end_date
        )

    # -------------------- Interpretation panel --------------------
    st.markdown("## 🧠 How the system understood your query")

    interpretation = {
        "intent": intent,
        "entities": entities,
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
        },
        "result": result
    }

    st.json(interpretation)

    # -------------------- Result panel --------------------
    st.markdown("## 📊 Result")

    # Scalar result
    if isinstance(result, (int, float)):
        st.success(f"Result: {result}")

    # List of transactions
    elif isinstance(result, list):
        if not result:
            st.warning("No matching transactions found.")
        else:
            st.dataframe(result, use_container_width=True)

    # Comparison / grouped results
    elif isinstance(result, dict):
        if not result:
            st.warning("No data available for comparison.")
        else:
            render_chart(result)

    else:
        st.write(result)

# -------------------- Footer --------------------
st.markdown(
    """
    <hr/>
    <p style="text-align:center; color:#9aa0a6; font-size:12px;">
    AlphaQuery · Hybrid NLP System · Final Year Project
    </p>
    """,
    unsafe_allow_html=True
)
