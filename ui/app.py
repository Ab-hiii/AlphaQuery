# ======================================================
# Streamlit Cloud PYTHONPATH FIX (REQUIRED)
# ======================================================
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# ======================================================
# Imports
# ======================================================
import streamlit as st
import pandas as pd

from core.intent_matcher import IntentMatcher
from core.entity_extractor import EntityExtractor
from core.date_parser import DateParser
from core.executor import Executor

# ======================================================
# Page config
# ======================================================
st.set_page_config(
    page_title="AlphaQuery",
    page_icon="🧠",
    layout="wide"
)

# ======================================================
# Load NLP pipeline (once per session)
# ======================================================
@st.cache_resource
def load_pipeline():
    return (
        IntentMatcher(),
        EntityExtractor(),
        DateParser(),
        Executor()
    )

intent_matcher, entity_extractor, date_parser, executor = load_pipeline()

# ======================================================
# Session state
# ======================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# ======================================================
# Data loading utilities
# ======================================================
REQUIRED_COLUMNS = {"date", "amount", "category", "merchant", "description"}

def load_transactions(file=None):
    if file:
        df = pd.read_csv(file)
    else:
        df = pd.read_csv("data/transactions.csv")

    if not REQUIRED_COLUMNS.issubset(df.columns):
        st.error(f"Dataset must contain columns: {REQUIRED_COLUMNS}")
        st.stop()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df

# ======================================================
# Sidebar – Data source + recent queries
# ======================================================
st.sidebar.header("📂 Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload transactions CSV",
    type=["csv"]
)

transactions_df = load_transactions(uploaded_file)

st.sidebar.subheader("🕘 Recent Queries")

if st.session_state.history:
    for idx, item in enumerate(st.session_state.history[:5]):
        label = f"{item['query'][:40]} ({item['intent']})"
        if st.sidebar.button(label, key=f"history_{idx}"):
            st.session_state.query_input = item["query"]
else:
    st.sidebar.caption("No recent queries")

if st.sidebar.button("🗑️ Clear History", key="clear_history"):
    st.session_state.history = []

# ======================================================
# Header
# ======================================================
st.markdown("## 🧠 AlphaQuery")
st.markdown(
    "<p style='color:#8B949E'>Ask questions about your expenses in plain English.</p>",
    unsafe_allow_html=True
)

# ======================================================
# Example queries
# ======================================================
with st.expander("💡 Example queries"):
    st.markdown(
        """
        - How much did I spend on food last month?
        - What is my biggest expense category?
        - Show my Zomato orders in January
        - Compare my spending this month vs last month
        """
    )

# ======================================================
# Query input
# ======================================================
query = st.text_input(
    "Enter your query",
    value=st.session_state.query_input,
    placeholder="e.g. How much did I spend on food last month?"
)

# ======================================================
# Run query
# ======================================================
if st.button("Analyze", key="analyze_btn") and query.strip():
    with st.spinner("Analyzing query..."):
        intent = intent_matcher.match_intent(query)
        entities = entity_extractor.extract(query)
        start_date, end_date = date_parser.parse(query)

        executor.df = transactions_df.copy()

        result = executor.execute(
            intent=intent["intent"],
            entities=entities,
            start_date=start_date,
            end_date=end_date
        )

    # Save query to history
    st.session_state.history.insert(
        0,
        {"query": query, "intent": intent["intent"]}
    )

    # ==================================================
    # Explainability
    # ==================================================
    with st.expander("🧠 How the system understood your query"):
        st.json({
            "intent": intent,
            "entities": entities,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        })

    # ==================================================
    # Confidence
    # ==================================================
    st.markdown("### 🔍 Confidence")
    st.progress(min(intent["score"], 1.0))

    # ==================================================
    # Result
    # ==================================================
    st.subheader("📊 Result")

    # --------------------------------------------------
    # CASE 1: LIST → table + charts
    # --------------------------------------------------
    if isinstance(result, list):

        if not result:
            st.info("No transactions found.")
        else:
            df = pd.DataFrame(result)
            df["date"] = pd.to_datetime(df["date"])

            # ---- Table ----
            st.markdown("### 🧾 Transactions")
            st.dataframe(
                df[["date", "amount", "category", "merchant"]],
                use_container_width=True
            )

            # ---- Time series ----
            st.markdown("### 📈 Spending Over Time")
            daily = (
                df.groupby(df["date"].dt.date)["amount"]
                .sum()
                .reset_index()
                .rename(columns={"date": "day"})
            )
            st.line_chart(daily.set_index("day"))

            # ---- Category breakdown ----
            if df["category"].nunique() > 1:
                st.markdown("### 🧩 Category Breakdown")
                cat_df = (
                    df.groupby("category")["amount"]
                    .sum()
                    .sort_values(ascending=False)
                )
                st.bar_chart(cat_df)

    # --------------------------------------------------
    # CASE 2: DICT → compare periods
    # --------------------------------------------------
    elif isinstance(result, dict):
        st.markdown("### 📊 Period Comparison")
        df = pd.DataFrame(
            list(result.items()),
            columns=["Period", "Amount"]
        )
        st.bar_chart(df.set_index("Period"))

    # --------------------------------------------------
    # CASE 3: SCALAR → metric
    # --------------------------------------------------
    else:
        st.metric("Result", result)
