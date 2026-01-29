"""
Interactive test runner for validating the NLP query system
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from evaluation.comprehensive_validator import ComprehensiveValidator


# Configuration
API_URL = "http://localhost:8000"
TEST_CASES_PATH = "data/test_cases.json"


def load_test_cases():
    """Load test cases from JSON file"""
    with open(TEST_CASES_PATH, "r") as f:
        return json.load(f)


def run_single_test(query: str, validator: ComprehensiveValidator):
    """Run a single query through the API and validate"""
    try:
        response = requests.get(f"{API_URL}/query", params={"q": query}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def display_comparison(expected: dict, actual: dict, validation: dict):
    """Display side-by-side comparison of expected vs actual"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Expected")
        st.json(expected)
    
    with col2:
        st.markdown("### 🔍 Actual")
        st.json(actual)
    
    # Validation results
    st.markdown("### ✅ Validation Results")
    
    # Overall status
    if validation["passed"]:
        st.success("✅ TEST PASSED")
    else:
        st.error("❌ TEST FAILED")
    
    # Component status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if validation["intent_match"]:
            st.success("✅ Intent")
        else:
            st.error("❌ Intent")
    
    with col2:
        if validation["entity_match"]:
            st.success("✅ Entities")
        else:
            st.error("❌ Entities")
    
    with col3:
        if validation["date_match"]:
            st.success("✅ Dates")
        else:
            st.error("❌ Dates")
    
    with col4:
        if validation["result_valid"]:
            st.success("✅ Result")
        else:
            st.error("❌ Result")
    
    # Issues
    if validation["issues"]:
        st.markdown("#### 🚨 Issues Found:")
        for issue in validation["issues"]:
            st.error(issue)
    
    # Warnings
    if validation["warnings"]:
        st.markdown("#### ⚠️ Warnings:")
        for warning in validation["warnings"]:
            st.warning(warning)


def main():
    st.set_page_config(page_title="Test Runner", layout="wide")
    
    st.title("🧪 AlphaQuery Test Suite")
    st.markdown("Comprehensive validation of intent, entities, dates, and results")
    
    # Initialize validator
    validator = ComprehensiveValidator()
    
    # Load test cases
    test_cases = load_test_cases()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Get unique intents
    all_intents = list(set(tc["expected"]["intent"]["intent"] for tc in test_cases))
    selected_intents = st.sidebar.multiselect(
        "Filter by Intent",
        options=all_intents,
        default=all_intents
    )
    
    # Show only failed tests
    show_only_failed = st.sidebar.checkbox("Show only failed tests", value=False)
    
    # Run all button
    if st.sidebar.button("🚀 Run All Tests", type="primary"):
        st.session_state.run_all = True
    
    # Stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Stats")
    st.sidebar.metric("Total Tests", len(test_cases))
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🧪 Test Runner", "📊 Summary", "➕ Add Test"])
    
    with tab1:
        # Run all tests if button clicked
        if st.session_state.get("run_all", False):
            run_all_tests(test_cases, validator, selected_intents)
            st.session_state.run_all = False
        
        # Individual test interface
        st.markdown("## Individual Test")
        
        # Test selector
        filtered_tests = [
            tc for tc in test_cases 
            if tc["expected"]["intent"]["intent"] in selected_intents
        ]
        
        test_queries = [tc["query"] for tc in filtered_tests]
        selected_query = st.selectbox(
            "Select a test query",
            options=test_queries,
            index=0 if test_queries else None
        )
        
        if selected_query and st.button("▶️ Run Selected Test"):
            # Find the test case
            test_case = next(tc for tc in filtered_tests if tc["query"] == selected_query)
            
            with st.spinner("Running query..."):
                actual_result = run_single_test(selected_query, validator)
            
            if actual_result:
                # Validate
                validation = validator.validate_query(
                    selected_query,
                    test_case["expected"],
                    actual_result
                )
                
                # Display
                st.markdown(f"### Query: *{selected_query}*")
                display_comparison(
                    test_case["expected"],
                    actual_result,
                    validation
                )
    
    with tab2:
        st.markdown("## Test Suite Summary")
        run_summary_tests(test_cases, validator, selected_intents, show_only_failed)
    
    with tab3:
        st.markdown("## Add New Test Case")
        add_test_interface()


def run_all_tests(test_cases, validator, selected_intents):
    """Run all tests and show summary"""
    st.markdown("## Running All Tests...")
    
    filtered_tests = [
        tc for tc in test_cases 
        if tc["expected"]["intent"]["intent"] in selected_intents
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    for i, test_case in enumerate(filtered_tests):
        status_text.text(f"Running test {i+1}/{len(filtered_tests)}: {test_case['query']}")
        
        actual_result = run_single_test(test_case["query"], validator)
        
        if actual_result:
            validation = validator.validate_query(
                test_case["query"],
                test_case["expected"],
                actual_result
            )
            
            results.append({
                "query": test_case["query"],
                "passed": validation["passed"],
                "intent_match": validation["intent_match"],
                "entity_match": validation["entity_match"],
                "date_match": validation["date_match"],
                "result_valid": validation["result_valid"],
                "issues": len(validation["issues"]),
                "warnings": len(validation["warnings"])
            })
        
        progress_bar.progress((i + 1) / len(filtered_tests))
    
    status_text.text("✅ All tests complete!")
    
    # Display summary
    st.markdown("---")
    st.markdown("## 📊 Test Results")
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Passed", f"{passed}/{total}")
    col2.metric("Failed", f"{total - passed}/{total}")
    col3.metric("Success Rate", f"{passed/total*100:.1f}%")
    
    # Detailed results table
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
    
    # Export results
    if st.button("💾 Export Results to JSON"):
        export_path = f"results/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("results", exist_ok=True)
        with open(export_path, "w") as f:
            json.dump(results, f, indent=2)
        st.success(f"Exported to {export_path}")


def run_summary_tests(test_cases, validator, selected_intents, show_only_failed):
    """Display summary of all tests without running them"""
    filtered_tests = [
        tc for tc in test_cases 
        if tc["expected"]["intent"]["intent"] in selected_intents
    ]
    
    if st.button("🔄 Refresh Summary"):
        st.rerun()
    
    # Group by intent
    intent_groups = {}
    for tc in filtered_tests:
        intent = tc["expected"]["intent"]["intent"]
        if intent not in intent_groups:
            intent_groups[intent] = []
        intent_groups[intent].append(tc)
    
    for intent, tests in intent_groups.items():
        with st.expander(f"**{intent}** ({len(tests)} tests)", expanded=True):
            for test in tests:
                st.markdown(f"- {test['query']}")


def add_test_interface():
    """Interface for adding new test cases"""
    with st.form("add_test_form"):
        st.markdown("### New Test Case")
        
        query = st.text_area("Query", placeholder="How much did I spend on food last month?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            intent = st.selectbox(
                "Expected Intent",
                options=["total_spend", "list_transactions", "average_spend", 
                        "compare_periods", "top_category"]
            )
            
            category = st.text_input("Expected Category (optional)")
            merchant = st.text_input("Expected Merchant (optional)")
            amount = st.number_input("Expected Amount Threshold (optional)", 
                                    min_value=0, value=0)
        
        with col2:
            start_date = st.date_input("Start Date (optional)")
            end_date = st.date_input("End Date (optional)")
            
            result_type = st.selectbox(
                "Result Type",
                options=["number", "list", "dict", "string"]
            )
            
            result_value = st.text_area("Expected Result (JSON format)")
        
        submitted = st.form_submit_button("➕ Add Test Case")
        
        if submitted and query:
            # Build test case
            new_test = {
                "query": query,
                "expected": {
                    "intent": {"intent": intent},
                    "entities": {
                        "category": category if category else None,
                        "merchant": merchant if merchant else None,
                        "amount": amount if amount > 0 else None
                    },
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "result": json.loads(result_value) if result_value else None
                }
            }
            
            # Load existing tests
            with open(TEST_CASES_PATH, "r") as f:
                test_cases = json.load(f)
            
            # Add new test
            test_cases.append(new_test)
            
            # Save
            with open(TEST_CASES_PATH, "w") as f:
                json.dump(test_cases, f, indent=2)
            
            st.success("✅ Test case added successfully!")
            st.rerun()


if __name__ == "__main__":
    main()