import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import base64
from model import (default_rates, default_util, default_settings, default_multi_state_config,
                  run_model, run_projection, summarize)
from valuation_tab import show_valuation_analysis

# Ora Living Brand Colors
ORA_COLORS = {
    'primary_dark': '#200E1B',
    'primary_cyan': '#00B7D8', 
    'teal': '#5F8996',
    'magenta': '#DD3F8E',
    'orange': '#DF9039',
    'white': '#FFFFFF',
    'light_gray': '#F8F9FA',
    'very_light_gray': '#FAFBFC',
    'professional_blue': '#00B7D8',  # Use primary cyan instead
    'success_green': '#107C10',
    'warning_orange': '#DF9039'  # Use Ora Living orange
}

# Configure page
st.set_page_config(
    page_title="Ora Living – Professional Financial Model", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add Google Fonts for Inter
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Load logo
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

logo_base64 = get_image_base64("Assets/ChatGPT Image Jul 15, 2025, 09_34_29 PM_1752640549696.png")

# Professional CSS with white background and readable fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* CSS Variables - Matching your app's design system */
    :root {
        --background: hsl(210, 20%, 98%);
        --foreground: #1a1a1a;
        --card: hsl(0, 0%, 100%);
        --card-foreground: #200E1B;
        --border: hsl(214, 32%, 91%);
        --primary: #00B7D8;
        --radius: 0.5rem;
        
        /* Ora Living Brand Colors */
        --ora-primary: #200E1B;
        --ora-highlight: #00B7D8;
        --ora-support-1: #5F8996;
        --ora-support-2: #DD3F8E;
        --ora-support-3: #DF9039;
        --ora-gray-50: hsl(210, 20%, 98%);
        --ora-gray-100: hsl(220, 14%, 93%);
    }
    
    /* Modern glass-morphism app background */
    .stApp {
        background: linear-gradient(135deg, 
            var(--ora-gray-50) 0%, 
            hsl(210, 30%, 96%) 25%,
            hsl(190, 20%, 97%) 50%,
            hsl(210, 25%, 97%) 75%,
            var(--ora-gray-50) 100%
        ) !important;
        color: var(--ora-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
    }
    
    .main, .block-container, .element-container {
        background: transparent !important;
        color: var(--ora-primary) !important;
    }
    
    /* Glass-morphism sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 0 24px 24px 0 !important;
    }
    
    /* Header with logo positioned top-right */
    .main-header {
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: #200E1B;
        position: relative;
        border: 2px solid #00B7D8;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        flex: 1;
    }
    
    .header-logo {
        flex-shrink: 0;
        margin-left: 2rem;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        font-family: 'Inter', sans-serif;
        color: white;
    }
    
    .main-subtitle {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
        font-family: 'Inter', sans-serif;
        color: #5F8996;
    }
    
    /* Glass-morphism data tables */
    .data-table {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 183, 216, 0.1);
    }
    
    .data-table th {
        background: rgba(0, 183, 216, 0.15);
        color: #200E1B;
        font-weight: 700;
        padding: 12px;
        text-align: left;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        border-bottom: 2px solid rgba(0, 183, 216, 0.3);
    }
    
    .data-table td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(0, 183, 216, 0.1);
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #200E1B;
    }
    
    .data-table tr:nth-child(even) {
        background-color: rgba(0, 183, 216, 0.05);
    }
    
    .data-table tr:hover {
        background-color: rgba(0, 183, 216, 0.2);
        transition: background-color 0.2s ease;
    }
    
    /* Scenario cards */
    .scenario-card {
        background: #FFFFFF;
        border: 2px solid {ORA_COLORS['light_gray']};
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .scenario-card:hover {
        border-color: #00B7D8;
        box-shadow: 0 4px 12px rgba(0,183,216,0.15);
        transform: translateY(-2px);
    }
    
    .scenario-card.selected {
        border-color: #00B7D8;
        background: linear-gradient(135deg, rgba(0,183,216,0.05) 0%, #FFFFFF 100%);
    }
    
    /* Glass-morphism metric cards - matching your dashboard */
    .metric-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 24px;
        padding: 2rem 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 183, 216, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--ora-highlight), var(--ora-support-2), var(--ora-support-1));
        border-radius: 24px 24px 0 0;
    }
    
    .metric-card:hover {
        box-shadow: 0 20px 64px rgba(0, 183, 216, 0.15);
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.85);
        border-color: rgba(0, 183, 216, 0.4);
    }
    
    .metric-card:hover::before {
        height: 4px;
        box-shadow: 0 0 20px rgba(0, 183, 216, 0.5);
    }
    
    .metric-title {
        font-size: 0.85rem;
        font-weight: 500;
        color: #6B7280;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        margin: 0;
        color: #200E1B;
    }
    
    .positive { color: {ORA_COLORS['success_green']}; }
    .negative { color: #DC2626; }
    .neutral { color: #5F8996; }
    
    /* Section headers */
    .section-header {
        color: #200E1B;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.4rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00B7D8;
    }
    
    .subsection-header {
        color: #0066CC;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1.5rem 0 0.8rem 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #F8F9FA;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: #200E1B;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #0066CC;
        color: white;
        box-shadow: 0 2px 4px rgba(0,120,212,0.3);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .status-success {
        background: rgba(16,124,16,0.1);
        color: {ORA_COLORS['success_green']};
        border: 1px solid rgba(16,124,16,0.2);
    }
    
    .status-warning {
        background: rgba(255,140,0,0.1);
        color: {ORA_COLORS['warning_orange']};
        border: 1px solid rgba(255,140,0,0.2);
    }
    
    .status-info {
        background: rgba(0,120,212,0.1);
        color: #0066CC;
        border: 1px solid rgba(0,120,212,0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0066CC, #00B7D8);
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,120,212,0.3);
    }
    
    /* Help widget */
    .help-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 320px;
        background: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        z-index: 1000;
        display: none;
    }
    
    .help-widget.open {
        display: block;
    }
    
    .help-header {
        background: #0066CC;
        color: white;
        padding: 1rem;
        border-radius: 12px 12px 0 0;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    .help-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 56px;
        height: 56px;
        background: #0066CC;
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,120,212,0.3);
        z-index: 1001;
    }
    
    /* Font consistency - all white text */
    body, .stMarkdown, .stText, p, div, span, label {
        font-family: 'Inter', sans-serif;
        color: #200E1B !important;
    }
    
    .stSelectbox label, .stNumberInput label, .stSlider label, .stCheckbox label {
        color: #200E1B !important;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    /* Input styling */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > input,
    .stSelectbox > div > div,
    .stSlider {
        border-color: #00B7D8 !important;
        color: #200E1B !important;
        background-color: #FFFFFF !important;
    }
    
    /* Selectbox styling - comprehensive */
    .stSelectbox > div > div > div {
        background-color: #FFFFFF !important;
        color: #200E1B !important;
        border: 2px solid #00B7D8 !important;
    }
    
    /* Dropdown menu options */
    .stSelectbox [role="listbox"] {
        background-color: #FFFFFF !important;
    }
    
    .stSelectbox [role="option"] {
        color: #200E1B !important;
        background-color: #FFFFFF !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: #F8F9FA !important;
        color: #200E1B !important;
    }
    
    /* Force dropdown text visibility */
    .stSelectbox div[data-baseweb="select"] > div {
        color: #200E1B !important;
        background-color: #FFFFFF !important;
    }
    
    .stSelectbox [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    
    /* Remove Streamlit header */
    .stApp > header {
        display: none;
    }
    
    /* Completely hide the file change notification bar */
    .stAlert, .stException, .stNotification, [data-testid=\"stNotificationContentInfo\"], [data-testid=\"stNotification\"] {
        display: none !important;
    }
    
    .main .block-container {
        padding-top: 1rem;
    }
    
    /* Comprehensive Sidebar styling */
    .stSidebar > div {
        background-color: #F8F9FA !important;
    }
    
    .stSidebar .stMarkdown, .stSidebar label, .stSidebar div, .stSidebar span {
        color: #200E1B !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sidebar selectbox styling */
    .stSidebar .stSelectbox > div > div > div {
        background-color: #FFFFFF !important;
        color: #200E1B !important;
        border: 2px solid #00B7D8 !important;
    }
    
    .stSidebar .stSelectbox [data-baseweb="select"] > div {
        color: #200E1B !important;
        background-color: #FFFFFF !important;
        font-weight: 500;
    }
    
    .stSidebar .stSelectbox [role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #00B7D8 !important;
    }
    
    .stSidebar .stSelectbox [role="option"] {
        color: #200E1B !important;
        background-color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    
    .stSidebar .stSelectbox [role="option"]:hover {
        background-color: #F8F9FA !important;
        color: #200E1B !important;
    }
    
    /* Sidebar headers */
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #200E1B !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sidebar number inputs */
    .stSidebar .stNumberInput > div > div > input {
        color: #200E1B !important;
        background-color: #FFFFFF !important;
        border: 2px solid #00B7D8 !important;
    }
    
    /* Sidebar sliders */
    .stSidebar .stSlider > div > div > div {
        background-color: #00B7D8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "states_config" not in st.session_state:
    st.session_state.states_config = default_multi_state_config()

if "scenario" not in st.session_state:
    st.session_state.scenario = {
        "rates": default_rates(),
        "util": default_util(), 
        "settings": default_settings()
    }

if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = "Custom"

states_config = st.session_state.states_config
sc = st.session_state.scenario

# Logo section at top-left
if logo_base64:
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem; padding: 1rem 0; border-bottom: 2px solid #00B7D8;">
        <img src="data:image/png;base64,{logo_base64}" width="80" style="margin-right: 1.5rem;">
        <div>
            <div style="font-size: 2.5rem; color: #200E1B; font-family: 'Inter', sans-serif; font-weight: 700; margin: 0;">ORA LIVING</div>
            <div style="color: #5F8996; font-family: 'Inter', sans-serif; font-size: 1.1rem; margin-top: 0.2rem;">Professional Multi-State Financial Model</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="margin-bottom: 1rem; padding: 1rem 0; border-bottom: 2px solid #00B7D8;">
        <div style="font-size: 2.5rem; color: #200E1B; font-family: 'Inter', sans-serif; font-weight: 700; margin: 0;">🏥 ORA LIVING</div>
        <div style="color: #5F8996; font-family: 'Inter', sans-serif; font-size: 1.1rem; margin-top: 0.5rem;">Professional Multi-State Financial Model</div>
    </div>
    """, unsafe_allow_html=True)

# Floating Help Widget
st.markdown("""
<div class="help-widget" id="help-widget">
    <div class="help-header">
        💡 Professional Help
        <button onclick="toggleHelp()" style="float: right; background: none; border: none; color: white; cursor: pointer;">✖</button>
    </div>
    <div style="padding: 1rem;">
        <p><strong>Quick Help Topics:</strong></p>
        <button onclick="showHelp('gpci')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">What is GPCI?</button>
        <button onclick="showHelp('states')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">State selection strategy</button>
        <button onclick="showHelp('billing')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">Billing codes explained</button>
        <button onclick="showHelp('results')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">Interpreting results</button>
    </div>
</div>

<button class="help-toggle" onclick="toggleHelp()" id="help-toggle">💡</button>

<script>
function toggleHelp() {
    const widget = document.getElementById('help-widget');
    const toggle = document.getElementById('help-toggle');
    
    if (widget.classList.contains('open')) {
        widget.classList.remove('open');
        toggle.innerHTML = '💡';
    } else {
        widget.classList.add('open');
        toggle.innerHTML = '✖';
    }
}

function showHelp(topic) {
    const helpContent = {
        'gpci': 'GPCI adjusts Medicare payments by geography:\\n\\n• Virginia: 1.00 (baseline)\\n• Florida: 1.05 (+5%)\\n• Texas: 1.03 (+3%)\\n• New York: 1.08 (+8%)\\n• California: 1.10 (+10%)',
        'states': 'Recommended expansion sequence:\\n\\n1. Virginia (Month 1) - Base\\n2. Florida (Month 12) - Medicare population\\n3. Texas (Month 18) - Scale opportunity\\n4. New York/California - Premium markets',
        'billing': 'Key revenue drivers:\\n\\n• 99454 ($52): Device supply (monthly)\\n• 99457 ($50): Care management\\n• 99458 ($43): Additional care (can bill multiple times)\\n\\nMultipliers show population averages.',
        'results': 'Good benchmarks:\\n\\n• EBITDA Margin: 30%+ good, 40%+ excellent\\n• Revenue PMPM: $150-250\\n• Patient Growth: 5-15% monthly\\n• Cash Flow: Positive by month 12-18'
    };
    
    alert(topic.charAt(0).toUpperCase() + topic.slice(1) + ' Help:\\n\\n' + helpContent[topic]);
}
</script>
""", unsafe_allow_html=True)

# Sidebar - Professional parameter controls
with st.sidebar:
    st.markdown(f'''
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #00B7D8, #DD3F8E); border-radius: 8px; margin-bottom: 1rem; color: white;">
        <h2 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: white;">🎛️ Model Controls</h2>
        <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.9; color: white;">Professional Financial Modeling</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initial Timeline - now editable
    st.markdown("")
    st.markdown(f'<div style="background: {ORA_COLORS["very_light_gray"]}; padding: 0.8rem; border-radius: 6px; border-left: 4px solid {ORA_COLORS["primary_cyan"]}; margin-bottom: 1rem;"><strong>📅 Project Timeline</strong></div>', unsafe_allow_html=True)
    sc["settings"]["months"] = st.number_input(
        "Project Timeline (Months)", 
        min_value=12, 
        max_value=120, 
        value=sc["settings"]["months"], 
        step=6,
        help="Total number of months to project forward"
    )
    
    # Scenario templates  
    st.markdown(f'<div style="background: {ORA_COLORS["very_light_gray"]}; padding: 0.8rem; border-radius: 6px; border-left: 4px solid {ORA_COLORS["magenta"]}; margin: 1.5rem 0 1rem 0;"><strong>📋 Choose Scenario</strong></div>', unsafe_allow_html=True)
    
    scenario_options = {
        "Conservative": {"growth": 0.05, "states": ["Virginia"], "multiplier": 1.0},
        "Balanced": {"growth": 0.10, "states": ["Virginia", "Florida"], "multiplier": 1.35},
        "Aggressive": {"growth": 0.15, "states": ["Virginia", "Florida", "Texas"], "multiplier": 2.0},
        "Custom": {"growth": sc["settings"]["monthly_growth"], "states": [], "multiplier": 1.35}
    }
    
    selected_scenario = st.selectbox(
        "Scenario Template:",
        options=list(scenario_options.keys()),
        index=3,
        help="Pre-configured scenarios you can modify"
    )
    
    if selected_scenario != st.session_state.selected_scenario:
        st.session_state.selected_scenario = selected_scenario
        if selected_scenario != "Custom":
            config = scenario_options[selected_scenario]
            sc["settings"]["monthly_growth"] = config["growth"]
            
            # Activate states
            for state in states_config:
                states_config[state]["active"] = state in config["states"]
            
            # Set multipliers
            for code in ["99458", "99439", "99427"]:
                if code in sc["rates"]:
                    sc["rates"][code]["multiplier"] = config["multiplier"]
    
    # Parameter summary table
    st.markdown(f'<div style="background: {ORA_COLORS["very_light_gray"]}; padding: 0.8rem; border-radius: 6px; border-left: 4px solid {ORA_COLORS["teal"]}; margin: 1.5rem 0 1rem 0;"><strong>⚙️ Current Parameters</strong></div>', unsafe_allow_html=True)
    
    param_data = {
        "Setting": ["Timeline", "Monthly Growth", "Initial Cash"],
        "Value": [
            f"{sc['settings']['months']} months",
            f"{sc['settings']['monthly_growth']:.1%}",
            f"${sc['settings']['initial_cash']:,.0f}"
        ]
    }
    
    param_df = pd.DataFrame(param_data)
    st.dataframe(param_df, use_container_width=True, hide_index=True)
    
    # Quick parameter edits
    st.markdown(f'<div style="background: {ORA_COLORS["very_light_gray"]}; padding: 0.8rem; border-radius: 6px; border-left: 4px solid {ORA_COLORS["primary_cyan"]}; margin: 1.5rem 0 1rem 0;"><strong>📝 Quick Adjustments</strong></div>', unsafe_allow_html=True)
    
    sc["settings"]["monthly_growth"] = st.select_slider(
        "Growth Rate", 
        options=[0.05, 0.08, 0.10, 0.12, 0.15, 0.20], 
        value=sc["settings"]["monthly_growth"],
        format_func=lambda x: f"{x:.1%}"
    )
    
    # Billing multipliers
    st.markdown(f'<div style="background: {ORA_COLORS["very_light_gray"]}; padding: 0.8rem; border-radius: 6px; border-left: 4px solid {ORA_COLORS["magenta"]}; margin: 1.5rem 0 1rem 0;"><strong>🔢 Billing Code Multipliers</strong></div>', unsafe_allow_html=True)
    
    billing_descriptions = {
        "99458": "Additional 20min RPM Sessions",
        "99439": "Additional CCM Sessions", 
        "99427": "Additional PCM Sessions"
    }
    
    for code in ["99458", "99439", "99427"]:
        if code in sc["rates"]:
            sc["rates"][code]["multiplier"] = st.slider(
                f"{code} - {billing_descriptions[code]}",
                1.0, 4.0,
                sc["rates"][code]["multiplier"],
                0.1,
                help=f"Population average billing frequency for {billing_descriptions[code].lower()}"
            )

# Main content tabs
tabs = st.tabs(["🏠 **Dashboard**", "📊 **Data Tables**", "📈 **Analysis & Charts**", "💰 **Valuation**", "⚙️ **Advanced Settings**"])

with tabs[0]:  # Dashboard
    st.markdown('<div class="section-header">📊 Executive Dashboard</div>', unsafe_allow_html=True)
    
    # Current scenario status
    active_states = [s for s, c in states_config.items() if c["active"]]
    scenario_status = "🔴 No states selected" if not active_states else f"🟢 {len(active_states)} states active"
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="status-indicator status-info">
            <strong>Current Scenario:</strong> {st.session_state.selected_scenario} | {scenario_status}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚀 **Run Model**", type="primary", use_container_width=True):
            if not active_states:
                st.error("⚠️ Please activate at least one state first!")
            else:
                with st.spinner("📊 Processing financial projections..."):
                    try:
                        active_states_dict = {k: v for k, v in states_config.items() if v["active"]}
                        gpci_dict = {k: v["gpci"] for k, v in active_states_dict.items()}
                        homes_dict = {k: v.get("initial_homes", 40) for k, v in active_states_dict.items()}
                        
                        df = run_projection(active_states_dict, gpci_dict, homes_dict, sc["rates"], sc["util"], sc["settings"])
                        st.session_state.multistate_df = df
                        
                        st.success(f"✅ Model complete! Generated {len(df)} rows of projections.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # State configuration table - editable
    st.markdown('<div class="subsection-header">🗺️ State Configuration</div>', unsafe_allow_html=True)
    
    # Create editable state table
    state_data = []
    for state, config in states_config.items():
        state_data.append({
            "State": state,
            "Activate": config["active"],
            "Launch Month": config["start_month"],
            "Initial Patients": config["initial_patients"],
            "GPCI Factor": config["gpci"],
            "Market Focus": {
                "Virginia": "Base market",
                "Florida": "Medicare-heavy",
                "Texas": "Scale opportunity", 
                "New York": "Premium rates",
                "California": "Highest GPCI"
            }.get(state, "")
        })
    
    state_df = pd.DataFrame(state_data)
    
    # Display as interactive table
    edited_states = st.data_editor(
        state_df,
        use_container_width=True,
        column_config={
            "Activate": st.column_config.CheckboxColumn("Activate", help="Include this state in projection"),
            "Launch Month": st.column_config.NumberColumn("Launch Month", min_value=1, max_value=120, step=1),
            "Initial Patients": st.column_config.NumberColumn("Initial Patients", min_value=10, max_value=500, step=10),
            "GPCI Factor": st.column_config.NumberColumn("GPCI Factor", format="%.3f", disabled=True),
            "Market Focus": st.column_config.Column("Market Focus", disabled=True)
        },
        hide_index=True
    )
    
    # Update states config from table
    for i, row in edited_states.iterrows():
        state = row["State"]
        if state in states_config:
            states_config[state]["active"] = row["Activate"]
            states_config[state]["start_month"] = row["Launch Month"]
            states_config[state]["initial_patients"] = row["Initial Patients"]
    
    # Show results if available
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        st.markdown('<div class="subsection-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
        
        # Calculate metrics
        final_patients = df[df["Month"] == df["Month"].max()]["Total Patients"].sum()
        total_revenue = df["Total Revenue"].sum()
        total_ebitda = df["EBITDA"].sum()
        ebitda_margin = (total_ebitda / total_revenue * 100) if total_revenue > 0 else 0
        total_capex = df["Dev Capex"].sum() + df["Infrastructure Capex"].sum()
        final_cash = df[df["Month"] == df["Month"].max()]["Cash Balance"].sum()
        
        # Display metrics in professional cards
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        metrics = [
            ("Total Patients", f"{final_patients:,.0f}", "👥"),
            ("Total Revenue", f"${total_revenue:,.0f}", "💰"),
            ("Total EBITDA", f"${total_ebitda:,.0f}", "📊"),
            ("EBITDA Margin", f"{ebitda_margin:.1f}%", "📈"),
            ("Total CapEx", f"${total_capex:,.0f}", "🏗️"),
            ("Final Cash", f"${final_cash:,.0f}", "🏦")
        ]
        
        for col, (title, value, icon) in zip([col1, col2, col3, col4, col5, col6], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{icon} {title}</div>
                    <div class="metric-value neutral">{value}</div>
                </div>
                """, unsafe_allow_html=True)

with tabs[1]:  # Data Tables
    st.markdown('<div class="section-header">📊 Data Tables & Worksheets</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Table selector
        table_options = ["Monthly Projections", "State Summary", "Revenue by Code", "Billing Rates"]
        selected_table = st.selectbox("Choose Data View:", table_options, help="Select different data perspectives")
        
        if selected_table == "Monthly Projections":
            st.markdown("**📅 Monthly Financial Projections**")
            
            # Show key columns first
            key_cols = ["Month", "State", "Total Patients", "Total Revenue", "Total Costs", "EBITDA", "Cash Balance"]
            available_cols = [col for col in key_cols if col in df.columns]
            
            display_df = df[available_cols].copy()
            
            # Format for display
            for col in ["Total Revenue", "Total Costs", "EBITDA", "Cash Balance"]:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Option to see all columns
            if st.checkbox("Show All Data Columns"):
                st.dataframe(df, use_container_width=True)
        
        elif selected_table == "State Summary":
            st.markdown("**🏛️ State Performance Summary**")
            
            state_summary = df.groupby("State").agg({
                "Total Patients": ["first", "last"],
                "Total Revenue": "sum",
                "EBITDA": "sum",
                "Cash Balance": "last"
            }).round(0)
            
            # Flatten column names
            state_summary.columns = ["Initial Patients", "Final Patients", "Total Revenue", "Total EBITDA", "Final Cash"]
            state_summary = state_summary.reset_index()
            
            # Format currency columns
            for col in ["Total Revenue", "Total EBITDA", "Final Cash"]:
                state_summary[col] = state_summary[col].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(state_summary, use_container_width=True, hide_index=True)
        
        elif selected_table == "Revenue by Code":
            st.markdown("**💰 Revenue Analysis by Billing Code**")
            
            revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
            
            if revenue_cols:
                monthly_revenue = df.groupby("Month")[revenue_cols].sum().reset_index()
                
                # Clean column names for display
                clean_revenue = monthly_revenue.copy()
                for col in revenue_cols:
                    clean_name = col.replace('Rev_', '').replace('_', ' ').title()
                    clean_revenue = clean_revenue.rename(columns={col: clean_name})
                
                st.dataframe(clean_revenue, use_container_width=True, hide_index=True)
            else:
                st.info("Revenue by code data not available. Run the model first.")
        
        elif selected_table == "Billing Rates":
            st.markdown("**💵 Current Billing Rates & Configuration**")
            
            rates_df = pd.DataFrame(sc["rates"]).T.reset_index()
            rates_df = rates_df.rename(columns={"index": "Code"})
            
            # Show key columns
            display_cols = ["Code", "rate", "multiplier", "type"]
            rates_display = rates_df[display_cols].copy()
            
            edited_rates = st.data_editor(
                rates_display,
                use_container_width=True,
                column_config={
                    "rate": st.column_config.NumberColumn("Rate ($)", format="$%.2f"),
                    "multiplier": st.column_config.NumberColumn("Population Avg Multiplier", min_value=1.0, max_value=4.0, step=0.1, format="%.2f"),
                    "type": st.column_config.SelectboxColumn("Billing Type", options=["setup", "monthly", "once"])
                },
                hide_index=True
            )
            
            # Update rates in session state
            for _, row in edited_rates.iterrows():
                code = row["Code"]
                if code in sc["rates"]:
                    sc["rates"][code]["rate"] = row["rate"]
                    sc["rates"][code]["multiplier"] = row["multiplier"]
                    sc["rates"][code]["type"] = row["type"]
    
    else:
        st.info("📊 No data available. Please run the model first to generate data tables.")

with tabs[2]:  # Charts & Analysis
    st.markdown('<div class="section-header">📈 Visual Analysis & Charts</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Chart selector
        chart_options = ["Revenue Stacked Bar", "Patient Growth", "Financial Dashboard", "State Comparison", "Working Capital"]
        selected_chart = st.selectbox("Select Chart Type:", chart_options, help="Choose visualization type")
        
        if selected_chart == "Revenue Stacked Bar":
            st.markdown("**💰 Revenue Breakdown by Billing Code**")
            
            revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
            
            if revenue_cols:
                monthly_revenue = df.groupby("Month")[revenue_cols].sum().reset_index()
                
                # Create stacked bar chart
                fig = go.Figure()
                
                colors = [ORA_COLORS['primary_dark'], ORA_COLORS['primary_cyan'], ORA_COLORS['teal'], 
                         ORA_COLORS['magenta'], ORA_COLORS['orange'], '#8E44AD', '#E74C3C', '#27AE60']
                
                for i, col in enumerate(revenue_cols):
                    code_name = col.replace('Rev_', '').replace('_', ' ').title()
                    fig.add_trace(go.Bar(
                        x=monthly_revenue["Month"],
                        y=monthly_revenue[col],
                        name=code_name,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    title="Monthly Revenue by Billing Code",
                    xaxis_title="Month",
                    yaxis_title="Revenue ($)",
                    barmode='stack',
                    font=dict(family="Inter", size=12, color=ORA_COLORS['primary_dark']),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=500,
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
                )
                
                fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
                fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6')
                
                st.plotly_chart(fig, use_container_width=True)
        
        elif selected_chart == "Patient Growth":
            st.markdown("**👥 Patient Growth Trajectory**")
            
            monthly_patients = df.groupby("Month")["Total Patients"].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_patients["Month"],
                y=monthly_patients["Total Patients"],
                mode='lines+markers',
                name='Total Patients',
                line=dict(color=ORA_COLORS['primary_cyan'], width=3),
                marker=dict(size=6, color=ORA_COLORS['primary_cyan'])
            ))
            
            fig.update_layout(
                title="Patient Growth Over Time",
                xaxis_title="Month",
                yaxis_title="Number of Patients",
                font=dict(family="Inter", size=12, color=ORA_COLORS['primary_dark']),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
            fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6')
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif selected_chart == "Financial Dashboard":
            st.markdown("**📈 Comprehensive Financial Analysis**")
            
            consolidated = df.groupby("Month").agg({
                "Total Revenue": "sum",
                "Total Costs": "sum",
                "EBITDA": "sum",
                "Cash Balance": "sum"
            }).reset_index()
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Revenue vs Costs ($K)', 'EBITDA Trend ($K)', 'Cash Flow ($K)', 'EBITDA Margin (%)'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Revenue vs Costs
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["Total Revenue"]/1000, 
                          name="Revenue", line=dict(color=ORA_COLORS['primary_cyan'], width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["Total Costs"]/1000, 
                          name="Costs", line=dict(color=ORA_COLORS['magenta'], width=2)),
                row=1, col=1
            )
            
            # EBITDA
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["EBITDA"]/1000, 
                          name="EBITDA", line=dict(color=ORA_COLORS['success_green'], width=2)),
                row=1, col=2
            )
            
            # Cash Flow
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["Cash Balance"]/1000, 
                          name="Cash", line=dict(color=ORA_COLORS['professional_blue'], width=2)),
                row=2, col=1
            )
            
            # EBITDA Margin
            ebitda_margin = (consolidated["EBITDA"] / consolidated["Total Revenue"] * 100).fillna(0)
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=ebitda_margin, 
                          name="EBITDA Margin", line=dict(color=ORA_COLORS['teal'], width=2)),
                row=2, col=2
            )
            
            fig.update_layout(
                height=600,
                font=dict(family="Inter", size=10, color=ORA_COLORS['primary_dark']),
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif selected_chart == "State Comparison":
            st.markdown("**🏛️ State Performance Analysis**")
            
            state_totals = df.groupby("State").agg({
                "Total Revenue": "sum",
                "EBITDA": "sum",
                "Total Patients": "last"
            }).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=state_totals["State"],
                y=state_totals["Total Revenue"],
                name="Total Revenue",
                marker_color=ORA_COLORS['primary_cyan']
            ))
            
            fig.update_layout(
                title="Total Revenue by State",
                xaxis_title="State",
                yaxis_title="Revenue ($)",
                font=dict(family="Inter", size=12, color=ORA_COLORS['primary_dark']),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
            fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6')
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif selected_chart == "Working Capital":
            st.markdown("**💰 Working Capital Analysis**")
            
            # Show working capital components over time
            monthly_wc = df.groupby("Month").agg({
                "Accounts Receivable": "sum",
                "Accounts Payable": "sum", 
                "Net Working Capital": "sum",
                "Change in NWC": "sum"
            }).reset_index()
            
            fig = go.Figure()
            
            # A/R buildup
            fig.add_trace(go.Scatter(
                x=monthly_wc["Month"], 
                y=monthly_wc["Accounts Receivable"]/1000,
                name="Accounts Receivable", 
                line=dict(color=ORA_COLORS['primary_cyan'], width=3),
                fill='tonexty'
            ))
            
            # Net Working Capital
            fig.add_trace(go.Scatter(
                x=monthly_wc["Month"], 
                y=monthly_wc["Net Working Capital"]/1000,
                name="Net Working Capital", 
                line=dict(color=ORA_COLORS['magenta'], width=2)
            ))
            
            # Monthly change
            fig.add_trace(go.Bar(
                x=monthly_wc["Month"], 
                y=monthly_wc["Change in NWC"]/1000,
                name="Monthly WC Change", 
                marker_color=ORA_COLORS['teal'],
                opacity=0.6,
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Working Capital Buildup Over Time",
                xaxis_title="Month",
                yaxis_title="Working Capital ($000s)",
                yaxis2=dict(title="Monthly Change ($000s)", overlaying='y', side='right'),
                font=dict(family="Inter", size=12, color=ORA_COLORS['primary_dark']),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=500,
                hovermode='x unified'
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
            fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show working capital summary
            st.markdown("**📋 Working Capital Summary**")
            col1, col2, col3 = st.columns(3)
            
            final_ar = df["Accounts Receivable"].iloc[-1]
            final_nwc = df["Net Working Capital"].iloc[-1] 
            total_nwc_change = df["Change in NWC"].sum()
            
            with col1:
                st.metric("Final A/R", f"${final_ar:,.0f}", help="Outstanding receivables")
            with col2:
                st.metric("Final Net WC", f"${final_nwc:,.0f}", help="Total working capital tied up")  
            with col3:
                st.metric("Total WC Investment", f"${total_nwc_change:,.0f}", help="Total cash invested in working capital")
    
    else:
        st.info("📈 No data available. Please run the model first to generate visualizations.")

with tabs[3]:  # Valuation 
    st.markdown('<div class="section-header">💰 Valuation Analysis</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        show_valuation_analysis(df)
    else:
        st.info("👆 **Please run the model first** to see valuation analysis")
        
        # Show placeholder valuation framework
        st.markdown("### 🏢 Healthcare Technology Valuation Framework")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Valuation Methodologies:**
            - **DCF Analysis** - Discounted cash flow modeling
            - **Comparable Companies** - Public RPM/CCM providers  
            - **Revenue Multiples** - 3-8x for RPM, 4-10x for CCM
            - **Healthcare SaaS** - 10-25x revenue multiples
            """)
            
        with col2:
            st.markdown("""
            **Key Valuation Drivers:**
            - **Patient Growth Rate** - Sustainable acquisition
            - **Patient Retention** - Attrition/churn management
            - **Revenue Per Patient** - Billing optimization
            - **EBITDA Margins** - Operational efficiency
            """)
            
        # Sample comparable companies
        st.markdown("### 📊 Comparable Company Overview")
        
        sample_comps = pd.DataFrame({
            'Company': ['Teladoc Health', 'American Well', 'Dexcom', 'Health Catalyst'],
            'Market Cap ($B)': [2.4, 0.8, 32.1, 1.9],
            'Revenue Multiple': [0.9, 1.1, 10.7, 6.7],
            'Category': ['Telehealth Platform', 'Telehealth Platform', 'RPM Hardware', 'Health Analytics']
        })
        
        st.dataframe(sample_comps, use_container_width=True, hide_index=True)

with tabs[4]:  # Advanced Settings
    st.markdown('<div class="section-header">⚙️ Advanced Model Configuration</div>', unsafe_allow_html=True)
    
    st.info("🔧 **Power User Mode**: Advanced parameter editing and model customization")
    
    # Advanced parameter tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Financial Parameters:**")
        
        sc["settings"]["initial_cash"] = st.number_input(
            "Initial Cash ($)", 
            -10000000.0, 50000000.0, 
            float(sc["settings"]["initial_cash"]), 
            10000.0
        )
        
        sc["settings"]["overhead_base"] = st.number_input(
            "Base Overhead (Monthly $)", 
            0.0, 100000.0, 
            float(sc["settings"]["overhead_base"]), 
            1000.0
        )
        
        sc["settings"]["staffing_pmpm"] = st.number_input(
            "Staffing Cost PMPM ($)", 
            0.0, 200.0, 
            float(sc["settings"]["staffing_pmpm"]), 
            1.0
        )
    
    with col2:
        st.markdown("**📊 Utilization Rates:**")
        
        sc["util"]["collection_rate"] = st.slider(
            "Payment Collection Rate", 
            0.7, 1.0, 
            sc["util"]["collection_rate"], 
            0.01,
            format="%.1%"
        )
        
        sc["util"]["rpm_16day"] = st.slider(
            "99454 Device Supply Eligibility", 
            0.5, 1.0, 
            sc["util"]["rpm_16day"], 
            0.05,
            format="%.1%"
        )
        
        sc["util"]["rpm_20min"] = st.slider(
            "99457 Care Management Eligibility", 
            0.5, 1.0, 
            sc["util"]["rpm_20min"], 
            0.05,
            format="%.1%"
        )
    
    # Complete billing rates table - editable
    st.markdown("**💵 Complete Billing Configuration**")
    
    rates_df = pd.DataFrame(sc["rates"]).T.reset_index().rename(columns={"index": "Code"})
    
    edited_rates = st.data_editor(
        rates_df,
        use_container_width=True,
        column_config={
            "rate": st.column_config.NumberColumn("Rate ($)", format="$%.2f"),
            "multiplier": st.column_config.NumberColumn("Multiplier", min_value=1.0, max_value=4.0, step=0.1, format="%.2f"),
            "type": st.column_config.SelectboxColumn("Type", options=["setup", "monthly", "once"])
        },
        num_rows="dynamic"
    )
    
    # Update all rates
    sc["rates"] = {}
    for _, row in edited_rates.iterrows():
        code = row["Code"]
        sc["rates"][code] = {
            "rate": row["rate"],
            "type": row["type"],
            "multiplier": row.get("multiplier", 1.0)
        }
        # Preserve theoretical flag if it exists
        if "theoretical" in row and pd.notna(row["theoretical"]):
            sc["rates"][code]["theoretical"] = row["theoretical"]

# Export functionality
st.markdown("---")
st.markdown('<div class="section-header">📁 Professional Export Options</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Monthly_Projections', index=False)
            
            # State summary
            state_summary = df.groupby("State").agg({
                "Total Patients": ["first", "last"],
                "Total Revenue": "sum",
                "EBITDA": "sum"
            })
            state_summary.to_excel(writer, sheet_name='State_Performance')
            
            # Revenue by code
            revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
            if revenue_cols:
                monthly_revenue = df.groupby("Month")[revenue_cols].sum()
                monthly_revenue.to_excel(writer, sheet_name='Revenue_Analysis')
            
            # Model configuration
            config_df = pd.DataFrame([sc["settings"]])
            config_df.to_excel(writer, sheet_name='Model_Settings', index=False)
            
            # Billing rates
            rates_export = pd.DataFrame(sc["rates"]).T
            rates_export.to_excel(writer, sheet_name='Billing_Configuration')
        
        st.download_button(
            label="📊 **Download Professional Report**",
            data=output.getvalue(),
            file_name=f"ora_living_financial_model_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Download complete financial model with all worksheets"
        )
    else:
        st.info("Run the model to enable report export")

with col2:
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 **Download Data (CSV)**",
            data=csv,
            file_name=f"ora_projections_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download raw data for further analysis"
        )
    else:
        st.info("Run the model to enable data export")

with col3:
    if st.button("💾 **Save Configuration**", use_container_width=True, help="Save current model setup"):
        st.success("✅ Configuration saved! (Would save to user profile in production)")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1.5rem; color: #5F8996; font-family: 'Inter', sans-serif;">
    <strong>Ora Living Professional Financial Model</strong><br>
    <em>Advanced healthcare analytics for professional decision-making</em><br>
    <small>💡 Click the help button for modeling guidance and support</small>
</div>
""", unsafe_allow_html=True)