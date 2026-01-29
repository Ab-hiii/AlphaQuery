"""
Interactive test runner for validating the NLP query system
(SCHEMA-SAFE VERSION — FIXED)
"""

import streamlit as st
import requests
import json
import pandas as pd
import sys
import os

# ------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from evaluation.comprehensive_validator import ComprehensiveValidator

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
API_URL = "http://127.0.0.1:8000/query"
TEST_CASES_PATH = "data/test_cases.json"

# ------------------------------------------------------------------
# Helpers (SCHEMA ADAPTERS)
# ------------------------------------------------------------------
def load_test_cases():
    with open(TEST_CASES_PATH, "r") as f:
        return json.load(f)


def get_intent(tc):
    if "expected" in tc:
        intent = tc["expected"].get("intent")
        if isinstance(intent, dict):
            return intent.get("intent")
        return intent
    return tc.get("intent")


def normalize_expected(tc):
    if "expected" in tc:
        return tc["expected"]

    return {
        "intent": {"intent": tc.get("intent")},
        "entities": {
            "category": tc.get("category"),
            "merchant": tc.get("merchant"),
            "amount": tc.get("amount"),
        },
        "start_date": None,
        "end_date": None,
        "result": None,
    }


def run_single_test(query: str):
    try:
        # ✅ FIX: DO NOT append /query again
        res = requests.get(API_URL, params={"q": query}, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# ------------------------------------------------------------------
# UI helpers
# ------------------------------------------------------------------
def display_comparison(expected, actual, validation):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Expected")
        st.json(expected)

    with col2:
        st.markdown("### 🔍 Actual")
        st.json(actual)

    st.markdown("### ✅ Validation Results")

    if validation["passed"]:
        st.success("✅ TEST PASSED")
    else:
        st.error("❌ TEST FAILED")

    cols = st.columns(4)
    cols[0].metric("Intent", "✅" if validation["intent_match"] else "❌")
    cols[1].metric("Entities", "✅" if validation["entity_match"] else "❌")
    cols[2].metric("Dates", "✅" if validation["date_match"] else "❌")
    cols[3].metric("Result", "✅" if validation["result_valid"] else "❌")

    for issue in validation["issues"]:
        st.error(issue)

    for warning in validation["warnings"]:
        st.warning(warning)

# ------------------------------------------------------------------
# Main App
# ------------------------------------------------------------------
def main():
    st.title("🧪 AlphaQuery Test Runner")
    st.markdown("Schema-safe validation for the Expense NLP system")

    validator = ComprehensiveValidator()
    test_cases = load_test_cases()

    # Sidebar
    st.sidebar.header("🔍 Filters")

    all_intents = sorted(
        set(get_intent(tc) for tc in test_cases if get_intent(tc))
    )

    selected_intents = st.sidebar.multiselect(
        "Filter by Intent",
        options=all_intents,
        default=all_intents,
    )

    if st.sidebar.button("🚀 Run All Tests"):
        st.session_state.run_all = True

    tab1, tab2 = st.tabs(["🧪 Run Tests", "📊 Summary"])

    # ---------------- TAB 1 ----------------
    with tab1:
        filtered_tests = [
            tc for tc in test_cases if get_intent(tc) in selected_intents
        ]

        if st.session_state.get("run_all", False):
            results = []
            bar = st.progress(0)

            for i, tc in enumerate(filtered_tests):
                actual = run_single_test(tc["query"])
                if not actual:
                    continue

                expected = normalize_expected(tc)
                validation = validator.validate_query(
                    tc["query"], expected, actual
                )

                results.append({
                    "query": tc["query"],
                    "intent": get_intent(tc),
                    "passed": validation["passed"],
                })

                bar.progress((i + 1) / len(filtered_tests))

            st.success(
                f"✅ {sum(r['passed'] for r in results)}/{len(results)} tests passed"
            )
            st.dataframe(pd.DataFrame(results), use_container_width=True)
            st.session_state.run_all = False

        st.markdown("## Run Individual Test")

        queries = [tc["query"] for tc in filtered_tests]
        selected_query = st.selectbox("Select query", queries)

        if st.button("▶️ Run Selected"):
            tc = next(t for t in filtered_tests if t["query"] == selected_query)
            actual = run_single_test(selected_query)

            if actual:
                expected = normalize_expected(tc)
                validation = validator.validate_query(
                    selected_query, expected, actual
                )
                display_comparison(expected, actual, validation)

    # ---------------- TAB 2 ----------------
    with tab2:
        st.markdown("## Test Coverage Summary")
        summary = {}
        for tc in test_cases:
            summary[get_intent(tc)] = summary.get(get_intent(tc), 0) + 1

        for intent, count in summary.items():
            st.markdown(f"- **{intent}** → {count} tests")


if __name__ == "__main__":
    main()
