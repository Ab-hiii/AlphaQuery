import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def render_chart(data: dict):
    if not data:
        st.info("No data to compare.")
        return

    df = pd.DataFrame(
        list(data.items()),
        columns=["Period", "Amount"]
    )

    fig, ax = plt.subplots()
    ax.bar(df["Period"], df["Amount"])
    ax.set_ylabel("Amount")
    ax.set_title("Spending Comparison")

    st.pyplot(fig)