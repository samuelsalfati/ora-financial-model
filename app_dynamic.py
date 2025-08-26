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
    'light_gray': '#F8F9FA'
}

# Configure page
st.set_page_config(
    page_title="Ora Living – Dynamic Financial Model", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and display logo
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

logo_base64 = get_image_base64("Assets/ChatGPT Image Jul 15, 2025, 09_34_29 PM_1752640549696.png")

# Custom CSS with Ora Living branding and logo
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .main-header {{
        background: linear-gradient(135deg, {ORA_COLORS['magenta']} 0%, {ORA_COLORS['primary_cyan']} 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    
    .logo-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    
    .main-header h1 {{
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.95);
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }}
    
    .state-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border-left: 5px solid;
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .state-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 25px rgba(0,0,0,0.12);
    }}
    
    .state-card.active {{
        border-left-color: {ORA_COLORS['primary_cyan']};
        background: linear-gradient(135deg, rgba(0, 183, 216, 0.05) 0%, rgba(255, 255, 255, 1) 100%);
    }}
    
    .state-card.planned {{
        border-left-color: {ORA_COLORS['orange']};
    }}
    
    .state-card.disabled {{
        border-left-color: #E0E0E0;
        background: #F9F9F9;
        opacity: 0.7;
    }}
    
    .state-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }}
    
    .state-title {{
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: {ORA_COLORS['primary_dark']};
        margin: 0;
    }}
    
    .state-status {{
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }}
    
    .status-active {{
        background: {ORA_COLORS['primary_cyan']};
        color: white;
    }}
    
    .status-planned {{
        background: {ORA_COLORS['orange']};
        color: white;
    }}
    
    .status-disabled {{
        background: #E0E0E0;
        color: #999;
    }}
    
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border-top: 4px solid;
        margin: 1rem 0;
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        font-family: 'Inter', sans-serif;
    }}
    
    .metric-label {{
        font-size: 1rem;
        font-weight: 600;
        color: #666;
        margin: 0;
        font-family: 'Inter', sans-serif;
    }}
    
    .section-header {{
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid {ORA_COLORS['primary_cyan']};
        padding-bottom: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {ORA_COLORS['light_gray']};
        border-radius: 12px;
        padding: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 10px;
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {ORA_COLORS['primary_cyan']};
        color: white;
        box-shadow: 0 2px 8px rgba(0,183,216,0.3);
    }}
    
    body {{
        font-family: 'Inter', sans-serif;
        background-color: {ORA_COLORS['light_gray']};
    }}
    
    .main > div {{
        padding-top: 2rem;
    }}
</style>
""", unsafe_allow_html=True)

# Main header with logo
if logo_base64:
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" width="80" style="margin-right: 1rem;">
            <div>
                <h1>ORA LIVING</h1>
                <p>Dynamic Multi-State Financial Model</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 ORA LIVING</h1>
        <p>Dynamic Multi-State Financial Model</p>
    </div>
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

states_config = st.session_state.states_config
sc = st.session_state.scenario

# Sidebar controls
with st.sidebar:
    st.markdown('<div class="section-header">🎛️ Model Controls</div>', unsafe_allow_html=True)
    
    # Timeline
    sc["settings"]["months"] = st.slider("Projection Timeline (Months)", 12, 120, sc["settings"]["months"], 12)
    
    # Growth assumptions
    st.markdown("**Growth Assumptions**")
    sc["settings"]["monthly_growth"] = st.slider("Monthly Growth Rate (%)", 0.0, 0.30, sc["settings"]["monthly_growth"], 0.01)
    sc["settings"]["patients_per_home_growth"] = st.slider("Annual Patients/Home Growth", 0.0, 0.20, sc["settings"]["patients_per_home_growth"], 0.01)
    
    # Advanced toggles
    st.markdown("**Advanced Features**")
    sc["settings"]["include_theoretical"] = st.checkbox("Theoretical Billing Codes", sc["settings"]["include_theoretical"])
    sc["settings"]["include_pcm"] = st.checkbox("Principal Care Management", sc["settings"]["include_pcm"])
    
    # Billing multiplier quick adjustments
    st.markdown("**Billing Intensity**")
    intensity = st.selectbox("Care Intensity Level", ["Conservative", "Moderate", "Aggressive"], index=1)
    
    if intensity == "Conservative":
        multipliers = {"99458": 1.0, "99439": 1.0, "99427": 1.0}
    elif intensity == "Moderate":
        multipliers = {"99458": 1.35, "99439": 1.2, "99427": 1.15}
    else:  # Aggressive
        multipliers = {"99458": 2.5, "99439": 2.0, "99427": 2.0}
    
    for code, mult in multipliers.items():
        if code in sc["rates"]:
            sc["rates"][code]["multiplier"] = mult

# Main content tabs
tabs = st.tabs(["🗺️ Multi-State Dashboard", "📊 Financial Performance", "⚙️ State Configuration", "💰 Revenue Analysis", "📁 Export"])

with tabs[0]:  # Multi-State Dashboard
    st.markdown('<div class="section-header">🗺️ Multi-State Expansion Dashboard</div>', unsafe_allow_html=True)
    
    # State overview cards
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("### 🎯 State Expansion Plan")
        
        for state, config in states_config.items():
            status = "active" if config["active"] else "planned"
            status_class = f"status-{status}"
            
            is_enabled = st.checkbox(f"Enable {state}", config["active"], key=f"enable_{state}")
            states_config[state]["active"] = is_enabled
            
            if is_enabled:
                with st.expander(f"{state} Configuration", expanded=config["active"]):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        states_config[state]["start_month"] = st.number_input(
                            f"Start Month", 
                            1, 120, 
                            config["start_month"], 
                            key=f"start_{state}"
                        )
                        states_config[state]["initial_patients"] = st.number_input(
                            f"Initial Patients", 
                            10, 500, 
                            config["initial_patients"],
                            key=f"patients_{state}"
                        )
                    with col_b:
                        states_config[state]["gpci"] = st.number_input(
                            f"GPCI Factor", 
                            0.8, 1.2, 
                            config["gpci"],
                            0.01,
                            key=f"gpci_{state}"
                        )
    
    with col2:
        # Quick state metrics
        active_states = [s for s, c in states_config.items() if c["active"]]
        total_initial = sum(c["initial_patients"] for c in states_config.values() if c["active"])
        avg_gpci = np.mean([c["gpci"] for c in states_config.values() if c["active"]]) if active_states else 1.0
        
        st.markdown("### 📈 Quick Metrics")
        
        metrics_html = f"""
        <div class="metric-card" style="border-top-color: {ORA_COLORS['primary_cyan']};">
            <div class="metric-label">Active States</div>
            <div class="metric-value" style="color: {ORA_COLORS['primary_cyan']};">{len(active_states)}</div>
        </div>
        
        <div class="metric-card" style="border-top-color: {ORA_COLORS['magenta']};">
            <div class="metric-label">Initial Patient Pool</div>
            <div class="metric-value" style="color: {ORA_COLORS['magenta']};">{total_initial:,}</div>
        </div>
        
        <div class="metric-card" style="border-top-color: {ORA_COLORS['teal']};">
            <div class="metric-label">Average GPCI</div>
            <div class="metric-value" style="color: {ORA_COLORS['teal']};">{avg_gpci:.3f}</div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 🚀 Actions")
        
        if st.button("🔄 Reset to Defaults", type="secondary"):
            st.session_state.states_config = default_multi_state_config()
            st.experimental_rerun()
        
        if st.button("▶️ Run Multi-State Model", type="primary"):
            # Run the multi-state projection
            try:
                active_states_dict = {k: v for k, v in states_config.items() if v["active"]}
                gpci_dict = {k: v["gpci"] for k, v in active_states_dict.items()}
                homes_dict = {k: 40 for k in active_states_dict.keys()}  # Default homes
                
                df = run_projection(
                    active_states_dict, 
                    gpci_dict, 
                    homes_dict, 
                    sc["rates"], 
                    sc["util"], 
                    sc["settings"]
                )
                
                st.session_state.multistate_df = df
                st.success(f"✅ Model completed! Generated projections for {len(active_states)} states over {sc['settings']['months']} months.")
                
            except Exception as e:
                st.error(f"❌ Model error: {e}")

# Display multi-state results if available
if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
    df = st.session_state.multistate_df
    
    # Beautiful multi-state charts
    st.markdown('<div class="section-header">📊 Multi-State Performance</div>', unsafe_allow_html=True)
    
    # Revenue by state
    state_revenue = df.groupby("State")["Total Revenue"].sum().sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            x=state_revenue.index,
            y=state_revenue.values,
            color=state_revenue.values,
            color_continuous_scale=[[0, ORA_COLORS['teal']], [1, ORA_COLORS['primary_cyan']]],
            title="Total Revenue by State"
        )
        fig1.update_layout(
            font=dict(family="Inter"),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Patient growth over time by state
        fig2 = px.line(
            df, 
            x="Month", 
            y="Total Patients", 
            color="State",
            title="Patient Growth by State"
        )
        fig2.update_layout(
            font=dict(family="Inter"),
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed monthly performance
    st.markdown("### Monthly Performance Detail")
    
    # Summary metrics by state
    summary_by_state = df.groupby("State").agg({
        "Total Patients": "last",
        "Total Revenue": "sum", 
        "EBITDA": "sum",
        "Cash Balance": "last"
    }).round(0)
    
    st.dataframe(summary_by_state, use_container_width=True)

with tabs[1]:  # Financial Performance
    st.markdown('<div class="section-header">📊 Financial Performance Analysis</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Consolidated financial metrics
        total_df = df.groupby("Month").agg({
            "Total Patients": "sum",
            "Total Revenue": "sum",
            "Total Costs": "sum", 
            "EBITDA": "sum",
            "Cash Balance": "sum"
        }).reset_index()
        
        # Beautiful financial dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue & Costs', 'EBITDA Trend', 'Patient Growth', 'Cash Flow'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue & Costs
        fig.add_trace(
            go.Scatter(x=total_df["Month"], y=total_df["Total Revenue"]/1000, 
                      name="Revenue ($K)", line=dict(color=ORA_COLORS['primary_cyan'], width=3)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=total_df["Month"], y=total_df["Total Costs"]/1000, 
                      name="Costs ($K)", line=dict(color=ORA_COLORS['magenta'], width=3)),
            row=1, col=1
        )
        
        # EBITDA
        fig.add_trace(
            go.Scatter(x=total_df["Month"], y=total_df["EBITDA"]/1000, 
                      name="EBITDA ($K)", line=dict(color=ORA_COLORS['teal'], width=3)),
            row=1, col=2
        )
        
        # Patients
        fig.add_trace(
            go.Scatter(x=total_df["Month"], y=total_df["Total Patients"], 
                      name="Patients", line=dict(color=ORA_COLORS['orange'], width=3)),
            row=2, col=1
        )
        
        # Cash
        fig.add_trace(
            go.Scatter(x=total_df["Month"], y=total_df["Cash Balance"]/1000, 
                      name="Cash ($K)", line=dict(color=ORA_COLORS['primary_dark'], width=3)),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            font=dict(family="Inter"),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("👈 Configure states and click 'Run Multi-State Model' to see financial performance!")

with tabs[2]:  # State Configuration
    st.markdown('<div class="section-header">⚙️ Detailed Configuration</div>', unsafe_allow_html=True)
    
    # Billing code multiplier controls
    st.markdown("### 🔢 Billing Code Multipliers")
    st.info("💡 Adjust population average multipliers for additional billing codes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "99458" in sc["rates"]:
            sc["rates"]["99458"]["multiplier"] = st.slider(
                "99458 (Additional RPM) Multiplier", 
                1.0, 4.0, 
                sc["rates"]["99458"]["multiplier"], 
                0.1
            )
    
    with col2:
        if "99439" in sc["rates"]:
            sc["rates"]["99439"]["multiplier"] = st.slider(
                "99439 (Additional CCM) Multiplier", 
                1.0, 3.0, 
                sc["rates"]["99439"]["multiplier"], 
                0.1
            )
    
    with col3:
        if "99427" in sc["rates"]:
            sc["rates"]["99427"]["multiplier"] = st.slider(
                "99427 (Additional PCM) Multiplier", 
                1.0, 3.0, 
                sc["rates"]["99427"]["multiplier"], 
                0.1
            )
    
    # Detailed rate editor
    st.markdown("### 💵 Billing Rates & Settings")
    
    rates_df = pd.DataFrame(sc["rates"]).T.reset_index().rename(columns={"index": "Code"})
    edited_rates = st.data_editor(
        rates_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "multiplier": st.column_config.NumberColumn(
                "Multiplier",
                min_value=1.0,
                max_value=4.0,
                step=0.1,
                format="%.2f"
            ),
            "rate": st.column_config.NumberColumn(
                "Rate ($)",
                format="$%.2f"
            )
        }
    )
    
    # Update rates
    sc["rates"] = {r["Code"]: {k: r[k] for k in edited_rates.columns if k != "Code"} for _, r in edited_rates.iterrows()}

with tabs[3]:  # Revenue Analysis
    st.markdown('<div class="section-header">💰 Revenue Deep Dive</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Revenue analysis by state and time
        st.markdown("### State-by-State Revenue Performance")
        
        # Create pivot table for heatmap
        revenue_pivot = df.pivot_table(
            values="Total Revenue", 
            index="State", 
            columns="Month", 
            fill_value=0
        )
        
        # Show sample months
        sample_months = [1, 12, 24, 36, 48, 60]
        available_months = [m for m in sample_months if m in revenue_pivot.columns]
        
        if available_months:
            st.dataframe(
                revenue_pivot[available_months].round(0),
                use_container_width=True
            )
    else:
        st.info("Run the multi-state model to see revenue analysis!")

with tabs[4]:  # Export
    st.markdown('<div class="section-header">📁 Export & Reports</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Excel export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Multi_State_Projections', index=False)
            
            # State summary
            state_summary = df.groupby("State").agg({
                "Total Patients": "last",
                "Total Revenue": "sum",
                "EBITDA": "sum", 
                "Cash Balance": "last"
            })
            state_summary.to_excel(writer, sheet_name='State_Summary')
            
            # Configuration
            pd.DataFrame([states_config]).T.to_excel(writer, sheet_name='State_Config')
            pd.DataFrame(sc["rates"]).T.to_excel(writer, sheet_name='Billing_Rates')
        
        st.download_button(
            label="📊 Download Multi-State Financial Model",
            data=output.getvalue(),
            file_name=f"ora_living_multistate_model_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Run the multi-state model to enable export functionality!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: {ORA_COLORS['teal']}; font-family: 'Inter', sans-serif;">
    <strong>Ora Living Dynamic Financial Model</strong><br>
    <em>Providing digital healthcare solutions to safeguard our future</em>
</div>
""", unsafe_allow_html=True)