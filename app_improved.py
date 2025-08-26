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
    'very_light_gray': '#FAFBFC'
}

# Billing code colors for charts
BILLING_CODE_COLORS = {
    'Rev_99453': ORA_COLORS['primary_dark'],  # Setup
    'Rev_99454': ORA_COLORS['primary_cyan'],  # Device supply
    'Rev_99457': ORA_COLORS['teal'],          # Base RPM
    'Rev_99458': ORA_COLORS['magenta'],       # Additional RPM  
    'Rev_99091': ORA_COLORS['orange'],        # MD Review
    'Rev_99490': '#8E44AD',                   # Base CCM
    'Rev_99439': '#E74C3C',                   # Additional CCM
    'Rev_99426': '#27AE60',                   # Base PCM
    'Rev_99427': '#F39C12',                   # Additional PCM
    'Rev_99495': '#3498DB',                   # TCM Moderate
    'Rev_99496': '#9B59B6',                   # TCM High
    'Rev_Theoretical': '#95A5A6'              # Theoretical codes
}

# Configure page
st.set_page_config(
    page_title="Ora Living – Enhanced Financial Model", 
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

# Custom CSS with WHITE BACKGROUND and Ora Living branding
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* WHITE BACKGROUND THROUGHOUT */
    .main {{
        background-color: {ORA_COLORS['white']};
    }}
    
    .stApp {{
        background-color: {ORA_COLORS['white']};
    }}
    
    .block-container {{
        background-color: {ORA_COLORS['white']};
        padding-top: 2rem;
    }}
    
    /* Header styling */
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
    
    /* State cards */
    .state-card {{
        background: {ORA_COLORS['white']};
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
        background: linear-gradient(135deg, rgba(0, 183, 216, 0.05) 0%, {ORA_COLORS['white']} 100%);
    }}
    
    .state-card.planned {{
        border-left-color: {ORA_COLORS['orange']};
        background: {ORA_COLORS['white']};
    }}
    
    /* Metric cards */
    .metric-card {{
        background: {ORA_COLORS['white']};
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
    
    /* Section headers */
    .section-header {{
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid {ORA_COLORS['primary_cyan']};
        padding-bottom: 0.5rem;
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {ORA_COLORS['very_light_gray']};
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
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: {ORA_COLORS['very_light_gray']};
    }}
    
    /* General text styling */
    body, .stMarkdown, .stText {{
        font-family: 'Inter', sans-serif;
        color: {ORA_COLORS['primary_dark']};
        background-color: {ORA_COLORS['white']};
    }}
    
    /* Ensure all backgrounds are white */
    .element-container, .stColumn, .stContainer {{
        background-color: {ORA_COLORS['white']};
    }}
    
    /* Info/warning boxes */
    .stInfo {{
        background-color: rgba(0, 183, 216, 0.1);
        border-left-color: {ORA_COLORS['primary_cyan']};
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
                <p>Enhanced Multi-State Financial Model</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 ORA LIVING</h1>
        <p>Enhanced Multi-State Financial Model</p>
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

# Sidebar controls with white background
with st.sidebar:
    st.markdown('<div class="section-header">🎛️ Model Controls</div>', unsafe_allow_html=True)
    
    # Timeline
    sc["settings"]["months"] = st.slider("Projection Timeline (Months)", 12, 120, sc["settings"]["months"], 12)
    
    # Growth assumptions
    st.markdown("**Growth Assumptions**")
    sc["settings"]["monthly_growth"] = st.slider("Monthly Growth Rate (%)", 0.0, 0.30, sc["settings"]["monthly_growth"], 0.01)
    
    # Billing multiplier controls
    st.markdown("**Billing Code Multipliers**")
    if "99458" in sc["rates"]:
        sc["rates"]["99458"]["multiplier"] = st.slider("99458 (Add'l RPM) Multiplier", 1.0, 4.0, sc["rates"]["99458"]["multiplier"], 0.1)
    if "99439" in sc["rates"]:
        sc["rates"]["99439"]["multiplier"] = st.slider("99439 (Add'l CCM) Multiplier", 1.0, 3.0, sc["rates"]["99439"]["multiplier"], 0.1)
    
    # Advanced toggles
    st.markdown("**Advanced Features**")
    sc["settings"]["include_theoretical"] = st.checkbox("Theoretical Billing Codes", sc["settings"]["include_theoretical"])
    sc["settings"]["include_pcm"] = st.checkbox("Principal Care Management", sc["settings"]["include_pcm"])

# Main content tabs
tabs = st.tabs(["🗺️ Multi-State Dashboard", "📊 Revenue by Billing Code", "📈 Financial Performance", "⚙️ Configuration", "📁 Export"])

with tabs[0]:  # Multi-State Dashboard
    st.markdown('<div class="section-header">🗺️ Multi-State Expansion Dashboard</div>', unsafe_allow_html=True)
    
    # Improved state configuration
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 🎯 State Configuration")
        
        for state, config in states_config.items():
            is_enabled = st.checkbox(f"**{state}**", config["active"], key=f"enable_{state}")
            states_config[state]["active"] = is_enabled
            
            if is_enabled:
                with st.expander(f"{state} Detailed Settings", expanded=config["active"]):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        states_config[state]["start_month"] = st.number_input(
                            f"Launch Month", 
                            1, 120, 
                            config["start_month"], 
                            key=f"start_{state}",
                            help=f"Month to start operations in {state}"
                        )
                    
                    with col_b:
                        states_config[state]["initial_patients"] = st.number_input(
                            f"Initial Patients", 
                            10, 500, 
                            config["initial_patients"],
                            key=f"patients_{state}",
                            help=f"Starting patient count for {state}"
                        )
                    
                    with col_c:
                        states_config[state]["gpci"] = st.number_input(
                            f"GPCI Factor", 
                            0.8, 1.2, 
                            config["gpci"],
                            0.01,
                            key=f"gpci_{state}",
                            help=f"Geographic Practice Cost Index for {state}"
                        )
                    
                    # Show state-specific info
                    if state == "Florida":
                        st.info("🏖️ Florida: Large retiree population, good for RPM/CCM growth")
                    elif state == "Texas":
                        st.info("🤠 Texas: Large population centers, significant scale opportunity")
                    elif state == "New York":
                        st.info("🗽 New York: High reimbursement rates, premium market")
                    elif state == "California":
                        st.info("☀️ California: Highest GPCI, tech-savvy population")
    
    with col2:
        # Calculate accurate weighted GPCI
        active_states = [(s, c) for s, c in states_config.items() if c["active"]]
        total_patients = sum(c["initial_patients"] for s, c in active_states)
        
        if total_patients > 0:
            weighted_gpci = sum(c["initial_patients"] * c["gpci"] for s, c in active_states) / total_patients
        else:
            weighted_gpci = 1.0
        
        st.markdown("### 📊 Key Metrics")
        
        metrics_html = f"""
        <div class="metric-card" style="border-top-color: {ORA_COLORS['primary_cyan']};">
            <div class="metric-label">Active States</div>
            <div class="metric-value" style="color: {ORA_COLORS['primary_cyan']};">{len(active_states)}</div>
        </div>
        
        <div class="metric-card" style="border-top-color: {ORA_COLORS['magenta']};">
            <div class="metric-label">Total Initial Patients</div>
            <div class="metric-value" style="color: {ORA_COLORS['magenta']};">{total_patients:,}</div>
        </div>
        
        <div class="metric-card" style="border-top-color: {ORA_COLORS['teal']};">
            <div class="metric-label">Weighted Average GPCI</div>
            <div class="metric-value" style="color: {ORA_COLORS['teal']};">{weighted_gpci:.3f}</div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
        
        # Launch button
        if st.button("🚀 **Run Multi-State Model**", type="primary", use_container_width=True):
            try:
                active_states_dict = {k: v for k, v in states_config.items() if v["active"]}
                if not active_states_dict:
                    st.error("❌ Please select at least one state!")
                else:
                    gpci_dict = {k: v["gpci"] for k, v in active_states_dict.items()}
                    homes_dict = {k: v.get("initial_homes", 40) for k, v in active_states_dict.items()}
                    
                    df = run_projection(
                        active_states_dict, 
                        gpci_dict, 
                        homes_dict, 
                        sc["rates"], 
                        sc["util"], 
                        sc["settings"]
                    )
                    
                    st.session_state.multistate_df = df
                    st.success(f"✅ Model completed! Analyzed {len(active_states_dict)} states over {sc['settings']['months']} months.")
            
            except Exception as e:
                st.error(f"❌ Model error: {e}")
                st.exception(e)

# Display results if available
if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
    df = st.session_state.multistate_df

with tabs[1]:  # Revenue by Billing Code
    st.markdown('<div class="section-header">📊 Revenue Breakdown by Billing Code</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Billing code revenue columns
        revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
        
        if revenue_cols:
            # Aggregate by month across all states
            monthly_revenue = df.groupby("Month")[revenue_cols].sum().reset_index()
            
            # Create stacked bar chart
            fig = go.Figure()
            
            for col in revenue_cols:
                code_name = col.replace('Rev_', '').replace('_', ' ')
                fig.add_trace(go.Bar(
                    x=monthly_revenue["Month"],
                    y=monthly_revenue[col],
                    name=code_name,
                    marker_color=BILLING_CODE_COLORS.get(col, '#95A5A6')
                ))
            
            fig.update_layout(
                title="Monthly Revenue by Billing Code (Stacked)",
                xaxis_title="Month",
                yaxis_title="Revenue ($)",
                barmode='stack',
                font=dict(family="Inter"),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=500,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary table of billing code performance
            st.markdown("### 💰 Billing Code Performance Summary")
            
            total_revenue_by_code = monthly_revenue[revenue_cols].sum()
            revenue_summary = pd.DataFrame({
                'Billing Code': [col.replace('Rev_', '') for col in revenue_cols],
                'Total Revenue': total_revenue_by_code.values,
                'Avg Monthly': total_revenue_by_code.values / len(monthly_revenue),
                'Percentage': (total_revenue_by_code.values / total_revenue_by_code.sum() * 100).round(1)
            }).sort_values('Total Revenue', ascending=False)
            
            st.dataframe(revenue_summary.style.format({
                'Total Revenue': '${:,.0f}',
                'Avg Monthly': '${:,.0f}',
                'Percentage': '{:.1f}%'
            }), use_container_width=True)
            
            # Show multiplier impact
            st.markdown("### 🔢 Multiplier Impact Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Current Multipliers:**")
                for code, config in sc["rates"].items():
                    mult = config.get("multiplier", 1.0)
                    if mult > 1.0:
                        st.write(f"• {code}: {mult:.2f}x")
            
            with col2:
                # Show top revenue generators
                top_codes = revenue_summary.head(5)
                fig2 = px.pie(
                    top_codes, 
                    values='Total Revenue', 
                    names='Billing Code',
                    title="Top 5 Revenue Sources",
                    color_discrete_sequence=list(BILLING_CODE_COLORS.values())
                )
                fig2.update_layout(height=400, font=dict(family="Inter"))
                st.plotly_chart(fig2, use_container_width=True)
        
        else:
            st.info("Billing code breakdown not available. Please run the model first.")
    
    else:
        st.info("👈 Configure states and run the model to see revenue breakdown by billing code!")

with tabs[2]:  # Financial Performance
    st.markdown('<div class="section-header">📈 Financial Performance</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Consolidated view across all states
        consolidated = df.groupby("Month").agg({
            "Total Patients": "sum",
            "Total Revenue": "sum",
            "Total Costs": "sum",
            "EBITDA": "sum",
            "Cash Balance": "sum"
        }).reset_index()
        
        # Multi-chart dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue vs Costs', 'Patient Growth', 'EBITDA Trend', 'Cash Flow'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue vs Costs
        fig.add_trace(
            go.Scatter(x=consolidated["Month"], y=consolidated["Total Revenue"]/1000, 
                      name="Revenue ($K)", line=dict(color=ORA_COLORS['primary_cyan'], width=3)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=consolidated["Month"], y=consolidated["Total Costs"]/1000, 
                      name="Costs ($K)", line=dict(color=ORA_COLORS['magenta'], width=3)),
            row=1, col=1
        )
        
        # Patient Growth
        fig.add_trace(
            go.Scatter(x=consolidated["Month"], y=consolidated["Total Patients"], 
                      name="Patients", line=dict(color=ORA_COLORS['teal'], width=3)),
            row=1, col=2
        )
        
        # EBITDA
        fig.add_trace(
            go.Scatter(x=consolidated["Month"], y=consolidated["EBITDA"]/1000, 
                      name="EBITDA ($K)", line=dict(color=ORA_COLORS['orange'], width=3)),
            row=2, col=1
        )
        
        # Cash Flow
        fig.add_trace(
            go.Scatter(x=consolidated["Month"], y=consolidated["Cash Balance"]/1000, 
                      name="Cash ($K)", line=dict(color=ORA_COLORS['primary_dark'], width=3)),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            font=dict(family="Inter"),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # State comparison
        st.markdown("### 🏛️ State-by-State Performance")
        
        state_summary = df.groupby("State").agg({
            "Total Patients": "last",
            "Total Revenue": "sum",
            "EBITDA": "sum",
            "Cash Balance": "last"
        }).round(0)
        
        st.dataframe(state_summary.style.format({
            'Total Patients': '{:,.0f}',
            'Total Revenue': '${:,.0f}',
            'EBITDA': '${:,.0f}',
            'Cash Balance': '${:,.0f}'
        }), use_container_width=True)
    
    else:
        st.info("👈 Run the multi-state model to see financial performance!")

with tabs[3]:  # Configuration
    st.markdown('<div class="section-header">⚙️ Detailed Configuration</div>', unsafe_allow_html=True)
    
    # Show current state configurations
    config_df = pd.DataFrame(states_config).T
    config_df.index.name = "State"
    config_df = config_df.reset_index()
    
    st.markdown("### 🗺️ Current State Configuration")
    st.dataframe(config_df, use_container_width=True)
    
    # Billing rates editor
    st.markdown("### 💵 Billing Rates & Multipliers")
    rates_df = pd.DataFrame(sc["rates"]).T.reset_index().rename(columns={"index": "Code"})
    edited_rates = st.data_editor(
        rates_df,
        use_container_width=True,
        column_config={
            "multiplier": st.column_config.NumberColumn(
                "Population Avg Multiplier",
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

with tabs[4]:  # Export
    st.markdown('<div class="section-header">📁 Export & Reports</div>', unsafe_allow_html=True)
    
    if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty:
        df = st.session_state.multistate_df
        
        # Enhanced Excel export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed_Projections', index=False)
            
            # Billing code revenue summary
            revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
            if revenue_cols:
                monthly_revenue = df.groupby("Month")[revenue_cols].sum()
                monthly_revenue.to_excel(writer, sheet_name='Revenue_by_Code')
            
            # State summary
            state_summary = df.groupby("State").agg({
                "Total Patients": ["first", "last"],
                "Total Revenue": "sum",
                "EBITDA": "sum",
                "Cash Balance": "last"
            })
            state_summary.to_excel(writer, sheet_name='State_Summary')
            
            # Configuration sheets
            pd.DataFrame([states_config]).T.to_excel(writer, sheet_name='State_Config')
            pd.DataFrame(sc["rates"]).T.to_excel(writer, sheet_name='Billing_Rates')
            pd.DataFrame([sc["settings"]]).to_excel(writer, sheet_name='Model_Settings', index=False)
        
        st.download_button(
            label="📊 **Download Complete Multi-State Model**",
            data=output.getvalue(),
            file_name=f"ora_living_enhanced_model_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    else:
        st.info("Run the multi-state model to enable export functionality!")

# Footer with white background
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: {ORA_COLORS['teal']}; font-family: 'Inter', sans-serif; background-color: {ORA_COLORS['white']};">
    <strong>Ora Living Enhanced Financial Model</strong><br>
    <em>Providing digital healthcare solutions to safeguard our future</em>
</div>
""", unsafe_allow_html=True)