"""
SENTINEL - Multi-Page Application
Main navigation hub for Historical Analysis and Live Agent Demo
"""
import streamlit as st

# Page configuration
st.set_page_config(
    layout="wide",
    page_title="SENTINEL AI Agent",
    page_icon="🎯",
    initial_sidebar_state="expanded",
)

# Define pages
historical_page = st.Page("pages/historical_analysis.py", title="📊 Historical Analysis", icon="📊")
live_demo_page = st.Page("pages/live_agent.py", title="⚡ Live Agent in Action", icon="⚡")

# Navigation
pg = st.navigation([historical_page, live_demo_page])

# Run the selected page
pg.run()
