import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from model import default_rates, default_util, default_settings, run_model, summarize, run_projection

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

# Custom CSS with Ora Living branding
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .main-header {{
        background: linear-gradient(135deg, {ORA_COLORS['magenta']} 0%, {ORA_COLORS['primary_cyan']} 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    .main-header h1 {{
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {ORA_COLORS['light_gray']};
        border-radius: 10px;
        padding: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px;
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {ORA_COLORS['primary_cyan']};
        color: white;
    }}
    
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid {ORA_COLORS['primary_cyan']};
        margin: 1rem 0;
    }}
    
    .section-header {{
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid {ORA_COLORS['primary_cyan']};
        padding-bottom: 0.5rem;
    }}
    
    .subsection-header {{
        color: {ORA_COLORS['teal']};
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        margin: 1.5rem 0 0.5rem 0;
    }}
    
    .stSelectbox > div > div {{
        border-color: {ORA_COLORS['primary_cyan']};
    }}
    
    .stSlider > div > div > div > div {{
        background-color: {ORA_COLORS['primary_cyan']};
    }}
    
    .stNumberInput > div > div > input {{
        border-color: {ORA_COLORS['primary_cyan']};
    }}
    
    body {{
        font-family: 'Inter', sans-serif;
    }}
</style>
""", unsafe_allow_html=True)

# Configure page
st.set_page_config(
    page_title="Ora Living – Financial Model", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main header with logo and branding
st.markdown(f"""
<div class="main-header">
    <h1>🏥 ORA LIVING</h1>
    <p>Investor-Grade Financial Model | Multi-State RPM/CCM Expansion</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "scenario" not in st.session_state:
    st.session_state.scenario = {
        "rates": default_rates(),
        "util": default_util(), 
        "settings": default_settings()
    }

sc = st.session_state.scenario

# Sidebar with beautiful styling
with st.sidebar:
    st.markdown('<div class="section-header">🎛️ Model Controls</div>', unsafe_allow_html=True)
    
    # Quick scenario selector
    st.markdown('<div class="subsection-header">Scenario</div>', unsafe_allow_html=True)
    scenario = st.selectbox(
        "Choose Scenario",
        ["Conservative", "Moderate", "Aggressive", "Custom"],
        index=1
    )
    
    if scenario == "Conservative":
        sc["settings"]["monthly_growth"] = 0.05
        sc["settings"]["include_theoretical"] = False
        for code in ["99458", "99439", "99427"]:
            if code in sc["rates"]:
                sc["rates"][code]["multiplier"] = 1.0
    elif scenario == "Moderate":
        sc["settings"]["monthly_growth"] = 0.10
        sc["settings"]["include_theoretical"] = False
        # Keep default multipliers
    elif scenario == "Aggressive": 
        sc["settings"]["monthly_growth"] = 0.15
        sc["settings"]["include_theoretical"] = True
        for code in ["99458", "99439", "99427"]:
            if code in sc["rates"]:
                sc["rates"][code]["multiplier"] = 2.0

    # Key settings
    st.markdown('<div class="subsection-header">Growth & Timeline</div>', unsafe_allow_html=True)
    sc["settings"]["months"] = st.slider("Projection Months", 12, 120, sc["settings"]["months"], 12)
    sc["settings"]["initial_patients"] = st.number_input("Initial Patients", 10, 1000, sc["settings"]["initial_patients"], 10)
    sc["settings"]["monthly_growth"] = st.slider("Monthly Growth %", 0.0, 0.30, sc["settings"]["monthly_growth"], 0.01)
    
    st.markdown('<div class="subsection-header">Advanced Features</div>', unsafe_allow_html=True)
    sc["settings"]["include_theoretical"] = st.checkbox("Theoretical Billing Codes", sc["settings"]["include_theoretical"])
    sc["settings"]["include_pcm"] = st.checkbox("Principal Care Management", sc["settings"]["include_pcm"])

# Main tabs
tabs = st.tabs(["📊 Executive Dashboard", "⚙️ Model Assumptions", "💰 Revenue Deep Dive", "📈 Financial Projections", "🌎 Multi-State Expansion", "📁 Export & Reports"])

# Run the model
try:
    df = run_model(sc["rates"], sc["util"], sc["settings"])
    summary = summarize(df)
except Exception as e:
    st.error(f"Model error: {e}")
    df = pd.DataFrame()
    summary = {"kpi": pd.DataFrame()}

with tabs[0]:  # Executive Dashboard
    st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        final_patients = df["Total Patients"].iloc[-1]
        total_revenue = df["Total Revenue"].sum()
        total_ebitda = df["EBITDA"].sum() if "EBITDA" in df.columns else 0
        final_cash = df["Cash Balance"].iloc[-1]
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {ORA_COLORS['primary_cyan']}; margin: 0;">Total Patients</h3>
                <h2 style="color: {ORA_COLORS['primary_dark']}; margin: 0.5rem 0 0 0;">{final_patients:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {ORA_COLORS['magenta']}; margin: 0;">Cumulative Revenue</h3>
                <h2 style="color: {ORA_COLORS['primary_dark']}; margin: 0.5rem 0 0 0;">${total_revenue:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {ORA_COLORS['teal']}; margin: 0;">Cumulative EBITDA</h3>
                <h2 style="color: {ORA_COLORS['primary_dark']}; margin: 0.5rem 0 0 0;">${total_ebitda:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {ORA_COLORS['orange']}; margin: 0;">Final Cash Balance</h3>
                <h2 style="color: {ORA_COLORS['primary_dark']}; margin: 0.5rem 0 0 0;">${final_cash:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Beautiful interactive charts with Ora Living colors
        st.markdown('<div class="section-header">📈 Financial Performance</div>', unsafe_allow_html=True)
        
        # Revenue & EBITDA Chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Revenue & Costs', 'EBITDA & Cash Flow'),
            vertical_spacing=0.1,
            specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
        )
        
        # Top chart - Revenue & Costs
        fig.add_trace(
            go.Scatter(x=df["Month"], y=df["Total Revenue"]/1000, 
                      name="Revenue ($K)", line=dict(color=ORA_COLORS['primary_cyan'], width=3)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df["Month"], y=df["Total Costs"]/1000, 
                      name="Costs ($K)", line=dict(color=ORA_COLORS['magenta'], width=3)),
            row=1, col=1
        )
        
        # Bottom chart - EBITDA & Cash
        ebitda_col = "EBITDA" if "EBITDA" in df.columns else "Total Revenue"
        fig.add_trace(
            go.Scatter(x=df["Month"], y=df[ebitda_col]/1000, 
                      name="EBITDA ($K)", line=dict(color=ORA_COLORS['teal'], width=3)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=df["Month"], y=df["Cash Balance"]/1000, 
                      name="Cash Balance ($K)", line=dict(color=ORA_COLORS['orange'], width=3)),
            row=2, col=1, secondary_y=True
        )
        
        fig.update_layout(
            height=600,
            font=dict(family="Inter", color=ORA_COLORS['primary_dark']),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Patient Growth Chart
        st.markdown('<div class="section-header">👥 Patient Growth</div>', unsafe_allow_html=True)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df["Month"], 
            y=df["Total Patients"],
            mode='lines+markers',
            name='Total Patients',
            line=dict(color=ORA_COLORS['primary_cyan'], width=4),
            marker=dict(size=6, color=ORA_COLORS['primary_cyan'])
        ))
        
        fig2.update_layout(
            title="Patient Growth Over Time",
            xaxis_title="Month",
            yaxis_title="Number of Patients", 
            font=dict(family="Inter", color=ORA_COLORS['primary_dark']),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)

with tabs[1]:  # Model Assumptions
    st.markdown('<div class="section-header">⚙️ Model Assumptions</div>', unsafe_allow_html=True)
    
    # Billing Codes with Multipliers
    st.markdown('<div class="subsection-header">Billing Code Rates & Multipliers</div>', unsafe_allow_html=True)
    st.info("💡 Multipliers represent population averages. E.g., 1.35x means 35% get additional sessions beyond base billing.")
    
    rates_df = pd.DataFrame(sc["rates"]).T.reset_index().rename(columns={"index": "Code"})
    edited_rates = st.data_editor(
        rates_df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "multiplier": st.column_config.NumberColumn(
                "Population Avg Multiplier",
                help="Average billing frequency across patient population",
                min_value=1.0,
                max_value=4.0,
                step=0.1
            )
        }
    )
    sc["rates"] = {r["Code"]: {k: r[k] for k in edited_rates.columns if k != "Code"} for _, r in edited_rates.iterrows()}
    
    # Utilization Rates
    st.markdown('<div class="subsection-header">Utilization & Eligibility Rates</div>', unsafe_allow_html=True)
    util_df = pd.DataFrame([sc["util"]])
    edited_util = st.data_editor(util_df, use_container_width=True)
    sc["util"] = edited_util.iloc[0].to_dict()

    # Settings
    st.markdown('<div class="subsection-header">Model Settings</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sc["settings"]["overhead_base"] = st.number_input("Base Overhead ($)", 0.0, 100000.0, float(sc["settings"]["overhead_base"]), 1000.0)
        sc["settings"]["staffing_pmpm"] = st.number_input("Staffing PMPM ($)", 0.0, 200.0, float(sc["settings"]["staffing_pmpm"]), 1.0)
    
    with col2:
        sc["settings"]["initial_cash"] = st.number_input("Initial Cash ($)", -10000000.0, 50000000.0, float(sc["settings"]["initial_cash"]), 10000.0)
        sc["settings"]["collection_rate"] = st.slider("Collection Rate", 0.7, 1.0, float(sc["util"].get("collection_rate", 0.95)), 0.01)
        sc["util"]["collection_rate"] = sc["settings"]["collection_rate"]
    
    with col3:
        sc["settings"]["initial_vendor"] = st.selectbox("Initial Vendor", ["Impilo", "CareSimple", "Ora"], index=0)
        migration_month = st.number_input("Migration Month (Optional)", 0, 120, int(sc["settings"].get("migration_month") or 0))
        sc["settings"]["migration_month"] = migration_month if migration_month > 0 else None

with tabs[2]:  # Revenue Deep Dive  
    st.markdown('<div class="section-header">💰 Revenue Analysis</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Revenue breakdown by code (would need to enhance model to track individual codes)
        st.markdown('<div class="subsection-header">Revenue Components</div>', unsafe_allow_html=True)
        
        # Per-patient metrics
        col1, col2 = st.columns(2)
        
        with col1:
            latest = df.iloc[-1]
            per_patient_revenue = latest["Per-Patient Revenue"] if "Per-Patient Revenue" in df.columns else 0
            per_patient_cost = latest["Per-Patient Cost"] if "Per-Patient Cost" in df.columns else 0
            per_patient_margin = per_patient_revenue - per_patient_cost
            
            metrics_data = {
                'Metric': ['Revenue PMPM', 'Cost PMPM', 'Margin PMPM'],
                'Value': [per_patient_revenue, per_patient_cost, per_patient_margin]
            }
            
            fig = px.bar(
                metrics_data, 
                x='Metric', 
                y='Value',
                color='Metric',
                color_discrete_map={
                    'Revenue PMPM': ORA_COLORS['primary_cyan'],
                    'Cost PMPM': ORA_COLORS['magenta'], 
                    'Margin PMPM': ORA_COLORS['teal']
                }
            )
            fig.update_layout(
                title="Per-Patient Monthly Economics",
                showlegend=False,
                font=dict(family="Inter"),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Show billing code multiplier impact
            st.markdown("**Billing Code Multipliers in Effect:**")
            for code, config in sc["rates"].items():
                if config.get("multiplier", 1.0) > 1.0:
                    st.write(f"• {code}: {config['multiplier']:.2f}x (${config['rate']:.2f} × {config['multiplier']:.2f} = ${config['rate'] * config['multiplier']:.2f})")

with tabs[3]:  # Financial Projections
    st.markdown('<div class="section-header">📈 Financial Projections</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Summary table
        st.dataframe(summary["kpi"], use_container_width=True)
        
        # Detailed monthly view
        st.markdown('<div class="subsection-header">Monthly Detail</div>', unsafe_allow_html=True)
        
        # Select columns to display
        display_cols = st.multiselect(
            "Choose columns to display:",
            df.columns.tolist(),
            default=["Month", "Total Patients", "Total Revenue", "Total Costs", "EBITDA", "Cash Balance"]
        )
        
        if display_cols:
            st.dataframe(df[display_cols], use_container_width=True)

with tabs[4]:  # Multi-State Expansion
    st.markdown('<div class="section-header">🌎 Multi-State Expansion</div>', unsafe_allow_html=True)
    st.info("🚧 Multi-state expansion controls coming soon! This will include state-by-state GPCI adjustments, start months, and regulatory variations.")
    
    # Preview of multi-state functionality
    st.markdown('<div class="subsection-header">Planned States & GPCI</div>', unsafe_allow_html=True)
    
    state_data = {
        'State': ['Virginia', 'Florida', 'Texas', 'New York', 'California'],
        'GPCI': [1.00, 1.05, 1.03, 1.08, 1.10],
        'Start Month': [1, 13, 25, 37, 49],
        'Status': ['Active', 'Planned', 'Planned', 'Planned', 'Planned']
    }
    
    st.dataframe(pd.DataFrame(state_data), use_container_width=True)

with tabs[5]:  # Export & Reports
    st.markdown('<div class="section-header">📁 Export & Reports</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Excel export
        st.markdown('<div class="subsection-header">Excel Export</div>', unsafe_allow_html=True)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Monthly_Projections', index=False)
            summary["kpi"].to_excel(writer, sheet_name='KPI_Summary', index=False)
            pd.DataFrame(sc["rates"]).T.to_excel(writer, sheet_name='Billing_Rates')
            pd.DataFrame([sc["util"]]).to_excel(writer, sheet_name='Utilization_Rates', index=False)
            pd.DataFrame([sc["settings"]]).to_excel(writer, sheet_name='Settings', index=False)
        
        st.download_button(
            label="📊 Download Complete Financial Model",
            data=output.getvalue(),
            file_name=f"ora_living_financial_model_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # PDF Report (placeholder)
        st.markdown('<div class="subsection-header">Executive Report</div>', unsafe_allow_html=True)
        st.info("📄 PDF executive report generation coming soon!")

# Footer with branding
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {ORA_COLORS['teal']}; font-family: 'Inter', sans-serif; font-size: 0.9rem;">
    <strong>Ora Living Financial Model</strong> | Providing digital healthcare solutions to safeguard our future
</div>
""", unsafe_allow_html=True)