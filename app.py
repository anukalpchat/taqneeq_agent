"""
SENTINEL AI Agent - Multi-Page Application
Advanced Financial Transaction Monitoring & Analysis Platform
"""
import streamlit as st

# Enhanced page configuration
st.set_page_config(
    layout="wide",
    page_title="SENTINEL AI Agent",
    page_icon="🎯",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        # SENTINEL AI Agent
        
        **Advanced Financial Transaction Monitoring Platform**
        
        SENTINEL uses AI-powered pattern detection to analyze financial transactions 
        in real-time, identifying anomalies, preventing fraud, and optimizing payment 
        routing for maximum profitability.
        
        **Key Features:**
        - Real-time transaction analysis
        - Autonomous decision-making
        - Pattern recognition and anomaly detection
        - Financial impact optimization
        """
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Global app styling */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Navigation styling */
    .stSidebar {
        background-color: #1f2937;
    }
    
    /* Enhanced navigation button styling */
    .stSelectbox > div > div {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
    }
    
    /* Professional title styling */
    .main-title {
        color: #a78bfa;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(167, 139, 250, 0.3);
    }
    
    .subtitle {
        color: #9ca3af;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Welcome header (only show on main page)
if 'selected_page' not in st.session_state:
    st.markdown('<h1 class="main-title">🎯 SENTINEL AI Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Advanced Financial Transaction Monitoring & Analysis Platform</p>', unsafe_allow_html=True)

# Define pages with enhanced descriptions
historical_page = st.Page(
    "pages/historical_analysis.py", 
    title="📊 Historical Analysis", 
    icon="📊",
    default=True
)

live_demo_page = st.Page(
    "pages/live_agent.py", 
    title="⚡ Live Agent Demo", 
    icon="⚡"
)

# Navigation with better organization
pg = st.navigation({
    "Analytics": [historical_page],
    "Live Demo": [live_demo_page]
})

# Track page selection
st.session_state['selected_page'] = True

# Run the selected page
pg.run()
