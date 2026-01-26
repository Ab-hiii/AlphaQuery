import streamlit as st
import pandas as pd


def render_card(title, value, subtitle=None):
    st.markdown(
        f"""
        <div class="card">
            <div class="muted">{title}</div>
            <div class="metric">{value}</div>
            {f"<div class='muted'>{subtitle}</div>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_result(data):
    intent = data["intent"]["intent"]
    result = data["result"]

    # ---------- Explainability Panel ----------
    with st.expander("🧠 How the system understood your query"):
        st.json({
            "intent": data["intent"],
            "entities": data["entities"],
            "date_range": {
                "start": data["start_date"],
                "end": data["end_date"]
            },
            "result": data["result"]
        })

    # ---------- Result Section ----------
    st.markdown("### 📊 Result")

    if intent == "total_spend":
        render_card(
            "Total Spend",
            f"₹ {result}"
        )

    elif intent == "average_spend":
        render_card(
            "Average Spend",
            f"₹ {round(result, 2)}"
        )

    elif intent == "top_category":
        render_card(
            "Highest Total Spend Category",
            result.capitalize() if result else "N/A"
        )

    elif intent == "list_transactions":
        if not result:
            st.info("No transactions found for this query.")
        else:
            df = pd.DataFrame(result)
            df["date"] = pd.to_datetime(df["date"]).dt.date
            st.dataframe(df, use_container_width=True)

    elif intent == "compare_periods":
        from charts import render_chart
        render_chart(result)

    else:
        st.json(result)