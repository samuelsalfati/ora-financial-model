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
    'excel_blue': '#0078D4',
    'excel_green': '#107C10',
    'excel_orange': '#FF8C00'
}

# Configure page - Excel-like experience
st.set_page_config(
    page_title="Ora Living – Excel-Style Financial Model", 
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load logo
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

logo_base64 = get_image_base64("Assets/ChatGPT Image Jul 15, 2025, 09_34_29 PM_1752640549696.png")

# Excel-inspired CSS with white background
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Pure white background everywhere */
    .main, .stApp, .block-container, .element-container {{
        background-color: {ORA_COLORS['white']} !important;
    }}
    
    .css-1d391kg {{
        background-color: {ORA_COLORS['very_light_gray']} !important;
    }}
    
    /* Header with gradient - like modern Excel */
    .excel-header {{
        background: linear-gradient(135deg, {ORA_COLORS['primary_cyan']} 0%, {ORA_COLORS['magenta']} 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,183,216,0.2);
    }}
    
    /* Excel-style data tables */
    .excel-table {{
        background: {ORA_COLORS['white']};
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .excel-table th {{
        background: {ORA_COLORS['excel_blue']};
        color: white;
        font-weight: 600;
        padding: 12px;
        text-align: left;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
    }}
    
    .excel-table td {{
        padding: 10px 12px;
        border-bottom: 1px solid #F3F4F6;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
    }}
    
    .excel-table tr:nth-child(even) {{
        background-color: #F9FAFB;
    }}
    
    .excel-table tr:hover {{
        background-color: #EBF8FF;
        transition: background-color 0.2s ease;
    }}
    
    /* Scenario cards - like Excel templates */
    .scenario-card {{
        background: {ORA_COLORS['white']};
        border: 2px solid {ORA_COLORS['light_gray']};
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    .scenario-card:hover {{
        border-color: {ORA_COLORS['primary_cyan']};
        box-shadow: 0 4px 12px rgba(0,183,216,0.15);
        transform: translateY(-2px);
    }}
    
    .scenario-card.selected {{
        border-color: {ORA_COLORS['primary_cyan']};
        background: linear-gradient(135deg, rgba(0,183,216,0.05) 0%, {ORA_COLORS['white']} 100%);
    }}
    
    /* Metric cards - Excel dashboard style */
    .metric-card {{
        background: {ORA_COLORS['white']};
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }}
    
    .metric-title {{
        font-size: 0.85rem;
        font-weight: 500;
        color: #6B7280;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        margin: 0;
    }}
    
    .metric-change {{
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.25rem;
    }}
    
    .positive {{ color: {ORA_COLORS['excel_green']}; }}
    .negative {{ color: #DC2626; }}
    .neutral {{ color: {ORA_COLORS['teal']}; }}
    
    /* Section headers - clean and professional */
    .section-header {{
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.4rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {ORA_COLORS['primary_cyan']};
    }}
    
    .subsection-header {{
        color: {ORA_COLORS['excel_blue']};
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1.5rem 0 0.8rem 0;
    }}
    
    /* Tabs - Excel ribbon style */
    .stTabs [data-baseweb="tab-list"] {{
        background: {ORA_COLORS['very_light_gray']};
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 6px;
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 8px 16px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {ORA_COLORS['excel_blue']};
        color: white;
        box-shadow: 0 2px 4px rgba(0,120,212,0.3);
    }}
    
    /* Status indicators */
    .status-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }}
    
    .status-success {{
        background: rgba(16,124,16,0.1);
        color: {ORA_COLORS['excel_green']};
        border: 1px solid rgba(16,124,16,0.2);
    }}
    
    .status-warning {{
        background: rgba(255,140,0,0.1);
        color: {ORA_COLORS['excel_orange']};
        border: 1px solid rgba(255,140,0,0.2);
    }}
    
    .status-info {{
        background: rgba(0,120,212,0.1);
        color: {ORA_COLORS['excel_blue']};
        border: 1px solid rgba(0,120,212,0.2);
    }}
    
    /* Progress bars - Excel style */
    .progress-container {{
        background: #F3F4F6;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {ORA_COLORS['excel_green']}, {ORA_COLORS['primary_cyan']});
        transition: width 0.5s ease;
    }}
    
    /* Buttons - modern Excel style */
    .stButton > button {{
        background: linear-gradient(135deg, {ORA_COLORS['excel_blue']}, {ORA_COLORS['primary_cyan']});
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,120,212,0.3);
    }}
    
    /* Data editor styling */
    .stDataFrame {{
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        overflow: hidden;
    }}
    
    /* Chat widget - floating like Excel help */
    .help-widget {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 320px;
        background: {ORA_COLORS['white']};
        border: 1px solid #D1D5DB;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        z-index: 1000;
        display: none;
    }}
    
    .help-widget.open {{
        display: block;
    }}
    
    .help-header {{
        background: {ORA_COLORS['excel_blue']};
        color: white;
        padding: 1rem;
        border-radius: 12px 12px 0 0;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }}
    
    .help-toggle {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 56px;
        height: 56px;
        background: {ORA_COLORS['excel_blue']};
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,120,212,0.3);
        z-index: 1001;
    }}
    
    .help-toggle:hover {{
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(0,120,212,0.4);
    }}
    
    /* Font consistency */
    body, .stMarkdown, .stText, p, div, span {{
        font-family: 'Inter', sans-serif;
        color: {ORA_COLORS['primary_dark']};
    }}
    
    /* Input styling */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stSlider {{
        border-color: {ORA_COLORS['excel_blue']};
    }}
    
    /* Remove any dark backgrounds */
    .stApp > header {{
        background: transparent;
    }}
    
    .stSidebar > div {{
        background-color: {ORA_COLORS['very_light_gray']};
    }}
</style>
""", unsafe_allow_html=True)

# Simple AI Help System
class ExcelHelper:
    def __init__(self):
        self.help_topics = {
            "gpci": {
                "title": "GPCI (Geographic Practice Cost Index)",
                "content": "GPCI adjusts Medicare payments based on local costs. Higher GPCI = more money per billing code.\n\n• Virginia: 1.00 (baseline)\n• Florida: 1.05 (+5%)\n• Texas: 1.03 (+3%)\n• New York: 1.08 (+8%)\n• California: 1.10 (+10%)\n\nLike Excel's VLOOKUP - it finds the right payment rate for your location!"
            },
            "states": {
                "title": "State Selection Strategy",
                "content": "**Recommended Expansion:**\n\n1. **Virginia** (Month 1) - Your home base\n2. **Florida** (Month 12) - Large Medicare population\n3. **Texas** (Month 18) - Scale opportunity\n4. **New York** (Month 30) - Premium rates\n5. **California** (Month 42) - Highest GPCI\n\n**Like building Excel scenarios** - start conservative, then expand!"
            },
            "billing": {
                "title": "Billing Code Revenue",
                "content": "**Main Revenue Drivers:**\n\n• **99454** ($52): Device supply (monthly)\n• **99457** ($50): Care management (monthly)\n• **99458** ($43): Additional care (can bill multiple times)\n\n**Multipliers = Excel's SUMPRODUCT:**\n• 1.0x = Standard billing\n• 1.35x = 35% get extra sessions\n• 2.0x = Intensive care model\n\nThink of it like Excel formulas calculating averages!"
            },
            "results": {
                "title": "Interpreting Your Results",
                "content": "**Good Benchmarks:**\n\n• **EBITDA Margin**: 30%+ is good, 40%+ excellent\n• **Revenue PMPM**: $150-250 per patient per month\n• **Patient Growth**: 5-15% monthly is realistic\n• **Cash Flow**: Positive by month 12-18\n\n**Like Excel pivot tables** - drill down into the numbers that matter!"
            }
        }
    
    def get_help(self, topic):
        return self.help_topics.get(topic, {
            "title": "General Help",
            "content": "I can help with GPCI, state selection, billing codes, and result interpretation. Just like Excel help but for healthcare financial modeling!"
        })

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

if "help_open" not in st.session_state:
    st.session_state.help_open = False

helper = ExcelHelper()
states_config = st.session_state.states_config
sc = st.session_state.scenario

# Header with logo - Excel ribbon style
if logo_base64:
    st.markdown(f"""
    <div class="excel-header">
        <img src="data:image/png;base64,{logo_base64}" width="50" style="margin-right: 1rem; vertical-align: middle;">
        <span style="font-size: 2rem; font-weight: 700;">ORA LIVING</span>
        <br>
        <span style="font-size: 1rem; opacity: 0.9;">Excel-Style Financial Model | Professional Healthcare Analytics</span>
    </div>
    """, unsafe_allow_html=True)

# Floating Help Widget
st.markdown(f"""
<div class="help-widget" id="help-widget">
    <div class="help-header">
        💡 Excel-Style Help
        <button onclick="toggleHelp()" style="float: right; background: none; border: none; color: white; cursor: pointer;">✖</button>
    </div>
    <div style="padding: 1rem;">
        <p><strong>Quick Help Topics:</strong></p>
        <button onclick="showHelp('gpci')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">What is GPCI?</button>
        <button onclick="showHelp('states')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">Which states to choose?</button>
        <button onclick="showHelp('billing')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">Billing codes explained</button>
        <button onclick="showHelp('results')" style="display: block; width: 100%; margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">How to read results</button>
    </div>
</div>

<button class="help-toggle" onclick="toggleHelp()" id="help-toggle">💡</button>

<script>
function toggleHelp() {{
    const widget = document.getElementById('help-widget');
    const toggle = document.getElementById('help-toggle');
    
    if (widget.classList.contains('open')) {{
        widget.classList.remove('open');
        toggle.innerHTML = '💡';
    }} else {{
        widget.classList.add('open');
        toggle.innerHTML = '✖';
    }}
}}

function showHelp(topic) {{
    // This would show specific help content
    alert('Help for: ' + topic + '\\n\\nIn a full version, this would show detailed help content.');
}}
</script>
""", unsafe_allow_html=True)

# Sidebar - Excel-style parameter panel
with st.sidebar:
    st.markdown('<div class="section-header">📊 Excel-Style Controls</div>', unsafe_allow_html=True)
    
    # Scenario templates
    st.markdown("**📋 Quick Scenarios** (Like Excel Templates)")
    
    scenario_options = {
        "Conservative": {"growth": 0.05, "states": ["Virginia"], "multiplier": 1.0},
        "Balanced": {"growth": 0.10, "states": ["Virginia", "Florida"], "multiplier": 1.35},
        "Aggressive": {"growth": 0.15, "states": ["Virginia", "Florida", "Texas"], "multiplier": 2.0},
        "Custom": {"growth": sc["settings"]["monthly_growth"], "states": [], "multiplier": 1.35}
    }
    
    selected_scenario = st.selectbox(
        "Choose Scenario Template:",
        options=list(scenario_options.keys()),
        index=3,
        help="Like Excel templates - pre-configured scenarios you can modify"
    )
    
    if selected_scenario != st.session_state.selected_scenario:
        st.session_state.selected_scenario = selected_scenario
        if selected_scenario != "Custom":
            # Apply scenario
            config = scenario_options[selected_scenario]
            sc["settings"]["monthly_growth"] = config["growth"]
            
            # Set states
            for state in states_config:
                states_config[state]["active"] = state in config["states"]
            
            # Set multipliers
            for code in ["99458", "99439", "99427"]:
                if code in sc["rates"]:
                    sc["rates"][code]["multiplier"] = config["multiplier"]
    
    # Parameter table - Excel-like
    st.markdown("**⚙️ Parameters** (Editable like Excel)")
    
    param_data = {
        "Setting": ["Timeline (months)", "Monthly Growth", "Initial Cash", "GPCI Base"],
        "Current Value": [
            sc["settings"]["months"],
            f"{sc['settings']['monthly_growth']:.1%}",
            f"${sc['settings']['initial_cash']:,.0f}",
            f"{sc['settings'].get('gpci', 1.0):.3f}"
        ],
        "Range": ["12-60", "5%-20%", "-$10M to $50M", "0.8-1.2"]
    }
    
    param_df = pd.DataFrame(param_data)
    st.dataframe(param_df, use_container_width=True, hide_index=True)
    
    # Direct parameter editing
    st.markdown("**📝 Quick Edits:**")
    
    sc["settings"]["months"] = st.select_slider(
        "Timeline", 
        options=[12, 24, 36, 48, 60], 
        value=sc["settings"]["months"]
    )
    
    sc["settings"]["monthly_growth"] = st.select_slider(
        "Growth Rate", 
        options=[0.05, 0.08, 0.10, 0.12, 0.15, 0.20], 
        value=sc["settings"]["monthly_growth"],
        format_func=lambda x: f"{x:.1%}"
    )
    
    # Billing multipliers
    st.markdown("**🔢 Billing Multipliers:**")
    
    for code in ["99458", "99439", "99427"]:
        if code in sc["rates"]:
            sc["rates"][code]["multiplier"] = st.slider(
                f"{code} Multiplier",
                1.0, 4.0,
                sc["rates"][code]["multiplier"],
                0.1,
                help=f"Average billing frequency for {code}"
            )

# Main content - Excel workbook style
tabs = st.tabs(["🏠 **Dashboard**", "📊 **Data Tables**", "📈 **Charts & Analysis**", "⚙️ **Advanced Settings**"])

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
                st.error("⚠️ Please select at least one state first!")
            else:
                with st.spinner("📊 Processing like Excel calculations..."):
                    try:
                        active_states_dict = {k: v for k, v in states_config.items() if v["active"]}
                        gpci_dict = {k: v["gpci"] for k, v in active_states_dict.items()}
                        homes_dict = {k: v.get("initial_homes", 40) for k, v in active_states_dict.items()}
                        
                        df = run_projection(active_states_dict, gpci_dict, homes_dict, sc["rates"], sc["util"], sc["settings"])
                        st.session_state.multistate_df = df
                        
                        st.success(f"✅ Model complete! Generated {len(df)} rows of data.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # State configuration table - Excel-like
    st.markdown('<div class="subsection-header">🗺️ State Configuration</div>', unsafe_allow_html=True)
    
    # Create editable state table
    state_data = []
    for state, config in states_config.items():
        state_data.append({
            "State": state,
            "Active": config["active"],
            "Start Month": config["start_month"],
            "Initial Patients": config["initial_patients"],
            "GPCI": config["gpci"],
            "Market Notes": {
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
            "Active": st.column_config.CheckboxColumn("Active", help="Include this state in projection"),
            "Start Month": st.column_config.NumberColumn("Start Month", min_value=1, max_value=60, step=1),
            "Initial Patients": st.column_config.NumberColumn("Initial Patients", min_value=10, max_value=500, step=10),
            "GPCI": st.column_config.NumberColumn("GPCI", format="%.3f", disabled=True),
            "Market Notes": st.column_config.Column("Market Notes", disabled=True)
        },
        hide_index=True
    )
    
    # Update states config from table
    for i, row in edited_states.iterrows():
        state = row["State"]
        if state in states_config:
            states_config[state]["active"] = row["Active"]
            states_config[state]["start_month"] = row["Start Month"]
            states_config[state]["initial_patients"] = row["Initial Patients"]
    
    # Show results if available
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        st.markdown('<div class="subsection-header">📈 Key Metrics</div>', unsafe_allow_html=True)
        
        # Calculate metrics
        final_patients = df[df["Month"] == df["Month"].max()]["Total Patients"].sum()
        total_revenue = df["Total Revenue"].sum()
        total_ebitda = df["EBITDA"].sum()
        ebitda_margin = (total_ebitda / total_revenue * 100) if total_revenue > 0 else 0
        final_cash = df[df["Month"] == df["Month"].max()]["Cash Balance"].sum()
        
        # Display metrics in Excel-style cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics = [
            ("Final Patients", f"{final_patients:,.0f}", "👥"),
            ("Total Revenue", f"${total_revenue:,.0f}", "💰"),
            ("Total EBITDA", f"${total_ebitda:,.0f}", "📊"),
            ("EBITDA Margin", f"{ebitda_margin:.1f}%", "📈"),
            ("Final Cash", f"${final_cash:,.0f}", "🏦")
        ]
        
        for col, (title, value, icon) in zip([col1, col2, col3, col4, col5], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{icon} {title}</div>
                    <div class="metric-value neutral">{value}</div>
                </div>
                """, unsafe_allow_html=True)

with tabs[1]:  # Data Tables
    st.markdown('<div class="section-header">📊 Data Tables (Excel View)</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Table selector
        table_options = ["Monthly Projections", "State Summary", "Revenue by Code", "Billing Rates"]
        selected_table = st.selectbox("Choose Data Table:", table_options, help="Like Excel worksheet tabs")
        
        if selected_table == "Monthly Projections":
            st.markdown("**📅 Monthly Financial Projections** (Full Dataset)")
            
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
            if st.checkbox("Show All Columns (Like Excel 'Unhide All')"):
                st.dataframe(df, use_container_width=True)
        
        elif selected_table == "State Summary":
            st.markdown("**🏛️ State-by-State Performance Summary**")
            
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
            st.markdown("**💰 Revenue Breakdown by Billing Code**")
            
            revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
            
            if revenue_cols:
                monthly_revenue = df.groupby("Month")[revenue_cols].sum().reset_index()
                
                # Clean column names
                clean_revenue = monthly_revenue.copy()
                for col in revenue_cols:
                    clean_name = col.replace('Rev_', '').replace('_', ' ').title()
                    clean_revenue = clean_revenue.rename(columns={col: clean_name})
                
                st.dataframe(clean_revenue, use_container_width=True, hide_index=True)
            else:
                st.info("Revenue by code data not available. Run the model first.")
        
        elif selected_table == "Billing Rates":
            st.markdown("**💵 Current Billing Rates & Multipliers** (Editable)")
            
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
                    "multiplier": st.column_config.NumberColumn("Multiplier", min_value=1.0, max_value=4.0, step=0.1, format="%.2f"),
                    "type": st.column_config.SelectboxColumn("Type", options=["setup", "monthly", "once"])
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
    st.markdown('<div class="section-header">📈 Charts & Visual Analysis</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Chart selector
        chart_options = ["Revenue Stacked Bar", "Patient Growth", "Financial Performance", "State Comparison"]
        selected_chart = st.selectbox("Choose Chart Type:", chart_options, help="Like Excel chart gallery")
        
        if selected_chart == "Revenue Stacked Bar":
            st.markdown("**💰 Revenue by Billing Code (Stacked Bar Chart)**")
            
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
                    font=dict(family="Inter", size=12),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=500,
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
                )
                
                fig.update_xaxis(showgrid=True, gridcolor='#F3F4F6')
                fig.update_yaxis(showgrid=True, gridcolor='#F3F4F6')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Revenue summary table
                st.markdown("**📊 Revenue Summary by Code:**")
                total_by_code = monthly_revenue[revenue_cols].sum().sort_values(ascending=False)
                
                summary_data = []
                for code, amount in total_by_code.items():
                    code_clean = code.replace('Rev_', '').replace('_', ' ').title()
                    percentage = (amount / total_by_code.sum()) * 100
                    summary_data.append({
                        "Billing Code": code_clean,
                        "Total Revenue": f"${amount:,.0f}",
                        "% of Total": f"{percentage:.1f}%"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        elif selected_chart == "Patient Growth":
            st.markdown("**👥 Patient Growth Over Time**")
            
            # Aggregate by month
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
                title="Patient Growth Trajectory",
                xaxis_title="Month",
                yaxis_title="Number of Patients",
                font=dict(family="Inter", size=12),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400
            )
            
            fig.update_xaxis(showgrid=True, gridcolor='#F3F4F6')
            fig.update_yaxis(showgrid=True, gridcolor='#F3F4F6')
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif selected_chart == "Financial Performance":
            st.markdown("**📈 Financial Performance Dashboard**")
            
            # Create multi-chart dashboard
            consolidated = df.groupby("Month").agg({
                "Total Revenue": "sum",
                "Total Costs": "sum",
                "EBITDA": "sum",
                "Cash Balance": "sum"
            }).reset_index()
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Revenue vs Costs', 'EBITDA Trend', 'Cash Flow', 'EBITDA Margin'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Revenue vs Costs
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["Total Revenue"]/1000, 
                          name="Revenue ($K)", line=dict(color=ORA_COLORS['primary_cyan'], width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["Total Costs"]/1000, 
                          name="Costs ($K)", line=dict(color=ORA_COLORS['magenta'], width=2)),
                row=1, col=1
            )
            
            # EBITDA
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["EBITDA"]/1000, 
                          name="EBITDA ($K)", line=dict(color=ORA_COLORS['excel_green'], width=2)),
                row=1, col=2
            )
            
            # Cash Flow
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=consolidated["Cash Balance"]/1000, 
                          name="Cash ($K)", line=dict(color=ORA_COLORS['excel_blue'], width=2)),
                row=2, col=1
            )
            
            # EBITDA Margin
            ebitda_margin = (consolidated["EBITDA"] / consolidated["Total Revenue"] * 100).fillna(0)
            fig.add_trace(
                go.Scatter(x=consolidated["Month"], y=ebitda_margin, 
                          name="EBITDA Margin (%)", line=dict(color=ORA_COLORS['teal'], width=2)),
                row=2, col=2
            )
            
            fig.update_layout(
                height=600,
                font=dict(family="Inter", size=10),
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif selected_chart == "State Comparison":
            st.markdown("**🏛️ State-by-State Comparison**")
            
            state_totals = df.groupby("State").agg({
                "Total Revenue": "sum",
                "EBITDA": "sum",
                "Total Patients": "last"
            }).reset_index()
            
            # Create comparison chart
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
                font=dict(family="Inter", size=12),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400
            )
            
            fig.update_xaxis(showgrid=True, gridcolor='#F3F4F6')
            fig.update_yaxis(showgrid=True, gridcolor='#F3F4F6')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # State performance table
            st.markdown("**State Performance Summary:**")
            display_states = state_totals.copy()
            display_states["Total Revenue"] = display_states["Total Revenue"].apply(lambda x: f"${x:,.0f}")
            display_states["EBITDA"] = display_states["EBITDA"].apply(lambda x: f"${x:,.0f}")
            display_states["Total Patients"] = display_states["Total Patients"].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(display_states, use_container_width=True, hide_index=True)
    
    else:
        st.info("📈 No data available. Please run the model first to generate charts.")

with tabs[3]:  # Advanced Settings
    st.markdown('<div class="section-header">⚙️ Advanced Settings (Power User Mode)</div>', unsafe_allow_html=True)
    
    st.info("🔧 **Excel Power User Mode**: Advanced parameter editing and model customization")
    
    # Advanced parameter tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Financial Parameters:**")
        
        financial_params = {
            "Parameter": ["Initial Cash", "Overhead Base", "Overhead Cap", "Staffing PMPM"],
            "Current": [
                f"${sc['settings']['initial_cash']:,.0f}",
                f"${sc['settings']['overhead_base']:,.0f}",
                f"${sc['settings']['overhead_cap']:,.0f}",
                f"${sc['settings']['staffing_pmpm']:.0f}"
            ],
            "Units": ["$", "$ monthly", "$ monthly", "$ per patient"]
        }
        
        financial_df = pd.DataFrame(financial_params)
        st.dataframe(financial_df, use_container_width=True, hide_index=True)
        
        # Direct editing
        sc["settings"]["initial_cash"] = st.number_input(
            "Initial Cash ($)", 
            -10000000.0, 50000000.0, 
            float(sc["settings"]["initial_cash"]), 
            10000.0
        )
        
        sc["settings"]["staffing_pmpm"] = st.number_input(
            "Staffing Cost PMPM ($)", 
            0.0, 200.0, 
            float(sc["settings"]["staffing_pmpm"]), 
            1.0
        )
    
    with col2:
        st.markdown("**📊 Utilization Rates:**")
        
        util_params = {
            "Code": ["99454 (Device)", "99457 (Care)", "99458 (Add'l)", "Collection Rate"],
            "Current": [
                f"{sc['util']['rpm_16day']:.1%}",
                f"{sc['util']['rpm_20min']:.1%}",
                f"{sc['util']['rpm_40min']:.1%}",
                f"{sc['util']['collection_rate']:.1%}"
            ],
            "Description": ["Device supply eligible", "Base care eligible", "Additional care", "Payment collection"]
        }
        
        util_df = pd.DataFrame(util_params)
        st.dataframe(util_df, use_container_width=True, hide_index=True)
        
        # Key utilization controls
        sc["util"]["collection_rate"] = st.slider(
            "Collection Rate", 
            0.7, 1.0, 
            sc["util"]["collection_rate"], 
            0.01,
            format="%.1%"
        )
    
    # Full billing rates table
    st.markdown("**💵 Complete Billing Rates Table** (Excel-style editing)")
    
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
        # Preserve any additional fields
        if "theoretical" in row and pd.notna(row["theoretical"]):
            sc["rates"][code]["theoretical"] = row["theoretical"]

# Export functionality
st.markdown("---")
st.markdown('<div class="section-header">📁 Export Options</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Excel export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Projections', index=False)
            
            # State summary
            state_summary = df.groupby("State").agg({
                "Total Patients": ["first", "last"],
                "Total Revenue": "sum",
                "EBITDA": "sum"
            })
            state_summary.to_excel(writer, sheet_name='State_Summary')
            
            # Revenue by code
            revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
            if revenue_cols:
                monthly_revenue = df.groupby("Month")[revenue_cols].sum()
                monthly_revenue.to_excel(writer, sheet_name='Revenue_by_Code')
            
            # Settings
            settings_df = pd.DataFrame([sc["settings"]])
            settings_df.to_excel(writer, sheet_name='Settings', index=False)
        
        st.download_button(
            label="📊 **Download Excel Workbook**",
            data=output.getvalue(),
            file_name=f"ora_living_model_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Download complete analysis as Excel file"
        )
    else:
        st.info("Run the model to enable Excel export")

with col2:
    # CSV export
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 **Download CSV Data**",
            data=csv,
            file_name=f"ora_projections_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download raw data as CSV file"
        )
    else:
        st.info("Run the model to enable CSV export")

with col3:
    # Save scenario
    if st.button("💾 **Save Scenario**", use_container_width=True, help="Save current settings as template"):
        scenario_data = {
            "states": states_config,
            "rates": sc["rates"],
            "settings": sc["settings"],
            "util": sc["util"]
        }
        
        # In a real app, this would save to a database or file
        st.success("✅ Scenario saved! (In production, this would save to your account)")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem; color: {ORA_COLORS['teal']}; font-family: 'Inter', sans-serif;">
    <strong>Ora Living Excel-Style Financial Model</strong><br>
    <em>Familiar Excel interface with professional healthcare analytics</em><br>
    <small>💡 Click the help button (bottom-right) for guidance, just like Excel Help!</small>
</div>
""", unsafe_allow_html=True)