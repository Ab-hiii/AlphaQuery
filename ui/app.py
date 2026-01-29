import streamlit as st
import pandas as pd
from datetime import datetime

# ---- Import NLP pipeline (local execution, no API) ----
from core.intent_matcher import IntentMatcher
from core.entity_extractor import EntityExtractor
from core.date_parser import DateParser
from core.executor import Executor

# ------------------------------------------------------
# Page config
# ------------------------------------------------------
st.set_page_config(
    page_title="AlphaQuery",
    page_icon="💸",
    layout="centered"
)

# ------------------------------------------------------
# Load NLP components (once)
# ------------------------------------------------------
@st.cache_resource
def load_pipeline():
    return (
        IntentMatcher(),
        EntityExtractor(),
        DateParser(),
        Executor()
    )

intent_matcher, entity_extractor, date_parser, executor = load_pipeline()

# ------------------------------------------------------
# Load transactions data
# ------------------------------------------------------
REQUIRED_COLUMNS = {"date", "amount", "category", "merchant", "description"}

def load_transactions(file=None):
    if file is not None:
        df = pd.read_csv(file)
    else:
        df = pd.read_csv("data/transactions.csv")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        st.error(f"CSV missing required columns: {missing}")
        st.stop()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    return df

# ------------------------------------------------------
# Sidebar – CSV Upload
# ------------------------------------------------------
st.sidebar.header("📂 Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload your transaction CSV",
    type=["csv"],
    help="CSV must contain: date, amount, category, merchant, description"
)

if uploaded_file:
    transactions_df = load_transactions(uploaded_file)
    st.sidebar.success("Using uploaded dataset")
else:
    transactions_df = load_transactions()
    st.sidebar.info("Using default dataset")

# ------------------------------------------------------
# Hero Section
# ------------------------------------------------------
st.markdown(
    """
    <style>
        .hero {
            padding: 1.5rem;
            border-radius: 12px;
            background: linear-gradient(135deg, #1f2933, #111827);
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown('<div class="hero">', unsafe_allow_html=True)

    st.title("💸 AlphaQuery")
    st.caption("Ask questions about your expenses in plain English")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Transactions",
        f"{len(transactions_df):,}"
    )

    col2.metric(
        "Date Range",
        f"{transactions_df['date'].min().date()} → {transactions_df['date'].max().date()}"
    )

    col3.metric(
        "Categories",
        transactions_df["category"].nunique()
    )

    col4.metric(
        "Merchants",
        transactions_df["merchant"].nunique()
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# Example queries
# ------------------------------------------------------
with st.expander("💡 Example queries"):
    st.markdown(
        """
        - How much did I spend on food last month?
        - What is my biggest expense category?
        - Show my Zomato orders in January
        - Compare my spending this month vs last month
        """
    )

# ------------------------------------------------------
# Query input
# ------------------------------------------------------
query = st.text_input(
    "Enter your query",
    placeholder="e.g. What is my biggest expense category?"
)

# ------------------------------------------------------
# Analyze button
# ------------------------------------------------------
if st.button("Analyze") and query:
    with st.spinner("Analyzing query..."):
        # ---- NLP pipeline ----
        intent = intent_matcher.match_intent(query)
        entities = entity_extractor.extract(query)
        start_date, end_date = date_parser.parse(query)

        # Inject custom dataframe into executor
        executor.df = transactions_df.copy()

        result = executor.execute(
            intent["intent"],
            entities,
            start_date,
            end_date
        )

    # --------------------------------------------------
    # Interpretation
    # --------------------------------------------------
    st.subheader("🧠 How the system understood your query")

    st.json({
        "intent": intent,
        "entities": entities,
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        },
        "result": result
    })

    # --------------------------------------------------
    # Confidence indicator
    # --------------------------------------------------
    confidence = intent["score"]

    st.markdown("### 🔍 Confidence")

    if confidence >= 0.7:
        color = "green"
    elif confidence >= 0.5:
        color = "orange"
    else:
        color = "red"

    st.progress(confidence)
    st.markdown(
        f"<span style='color:{color}'>Confidence score: {confidence:.2%}</span>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------
    st.subheader("📊 Result")

    if isinstance(result, list):
        st.dataframe(result)
    else:
        st.write(result)
