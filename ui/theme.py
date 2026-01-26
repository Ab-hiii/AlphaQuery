import streamlit as st

def apply_dark_theme():
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            background-color: #0E1117;
            color: #E6EDF3;
        }

        .stTextInput > div > div > input {
            background-color: #161B22;
            color: #E6EDF3;
        }

        .stButton button {
            background-color: #238636;
            color: white;
            border-radius: 6px;
            padding: 0.5em 1em;
        }

        .card {
            background-color: #161B22;
            padding: 1.2rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }

        .metric {
            font-size: 2.2rem;
            font-weight: bold;
        }

        .muted {
            color: #8B949E;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )