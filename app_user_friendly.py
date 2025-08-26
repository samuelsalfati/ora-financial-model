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
    'success': '#28a745',
    'warning': '#ffc107',
    'info': '#17a2b8'
}

# Configure page
st.set_page_config(
    page_title="Ora Living – User-Friendly Financial Model", 
    page_icon="🏥",
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

# Enhanced CSS with better UX
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Clean white background */
    .main, .stApp, .block-container {{
        background-color: {ORA_COLORS['white']};
    }}
    
    /* Welcome banner */
    .welcome-banner {{
        background: linear-gradient(135deg, {ORA_COLORS['primary_cyan']} 0%, {ORA_COLORS['magenta']} 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        color: white;
    }}
    
    /* Step indicators */
    .step-indicator {{
        display: flex;
        justify-content: center;
        margin: 2rem 0;
        gap: 1rem;
    }}
    
    .step {{
        background: {ORA_COLORS['light_gray']};
        border: 2px solid {ORA_COLORS['light_gray']};
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #666;
    }}
    
    .step.active {{
        background: {ORA_COLORS['primary_cyan']};
        border-color: {ORA_COLORS['primary_cyan']};
        color: white;
    }}
    
    .step.completed {{
        background: {ORA_COLORS['success']};
        border-color: {ORA_COLORS['success']};
        color: white;
    }}
    
    /* Quick action buttons */
    .quick-action {{
        background: {ORA_COLORS['white']};
        border: 2px solid {ORA_COLORS['primary_cyan']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .quick-action:hover {{
        background: rgba(0, 183, 216, 0.1);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,183,216,0.2);
    }}
    
    .quick-action.selected {{
        background: rgba(0, 183, 216, 0.1);
        border-color: {ORA_COLORS['primary_cyan']};
    }}
    
    /* Help tooltips */
    .help-tooltip {{
        background: {ORA_COLORS['info']};
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
        cursor: help;
    }}
    
    /* Progress indicators */
    .progress-bar {{
        width: 100%;
        height: 8px;
        background: {ORA_COLORS['light_gray']};
        border-radius: 4px;
        margin: 1rem 0;
    }}
    
    .progress-fill {{
        height: 100%;
        background: linear-gradient(90deg, {ORA_COLORS['primary_cyan']}, {ORA_COLORS['magenta']});
        border-radius: 4px;
        transition: width 0.3s ease;
    }}
    
    /* Status messages */
    .status-message {{
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }}
    
    .status-success {{
        background: rgba(40, 167, 69, 0.1);
        border-left: 4px solid {ORA_COLORS['success']};
        color: #155724;
    }}
    
    .status-warning {{
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid {ORA_COLORS['warning']};
        color: #856404;
    }}
    
    .status-info {{
        background: rgba(23, 162, 184, 0.1);
        border-left: 4px solid {ORA_COLORS['info']};
        color: #0c5460;
    }}
    
    /* Enhanced cards */
    .feature-card {{
        background: {ORA_COLORS['white']};
        border: 1px solid {ORA_COLORS['light_gray']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }}
    
    .feature-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    /* Improved typography */
    .section-title {{
        color: {ORA_COLORS['primary_dark']};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid {ORA_COLORS['primary_cyan']};
        padding-bottom: 0.5rem;
    }}
    
    .subsection-title {{
        color: {ORA_COLORS['teal']};
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1rem 0 0.5rem 0;
    }}
    
    /* Enhanced buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {ORA_COLORS['primary_cyan']}, {ORA_COLORS['magenta']});
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,183,216,0.3);
    }}
    
    /* Clean sidebar */
    .css-1d391kg {{
        background-color: {ORA_COLORS['very_light_gray']};
    }}
    
    /* Font consistency */
    body, .stMarkdown, .stText, div {{
        font-family: 'Inter', sans-serif;
        color: {ORA_COLORS['primary_dark']};
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state with guided tour flag
if "guided_tour_shown" not in st.session_state:
    st.session_state.guided_tour_shown = False
    st.session_state.current_step = 1

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

# Welcome banner with logo
if logo_base64:
    st.markdown(f"""
    <div class="welcome-banner">
        <img src="data:image/png;base64,{logo_base64}" width="60" style="margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 2.5rem;">ORA LIVING</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">User-Friendly Multi-State Financial Model</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Build investor-grade projections in 3 simple steps</p>
    </div>
    """, unsafe_allow_html=True)

# Quick Start Guide - always visible at top
with st.container():
    st.markdown('<div class="section-title">🚀 Quick Start Guide</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 **Conservative Growth**", help="Start with Virginia only, conservative assumptions", use_container_width=True):
            # Reset to conservative scenario
            states_config["Virginia"]["active"] = True
            for state in ["Florida", "Texas", "New York", "California"]:
                states_config[state]["active"] = False
            sc["settings"]["monthly_growth"] = 0.05
            sc["settings"]["include_theoretical"] = False
            sc["rates"]["99458"]["multiplier"] = 1.0
            sc["rates"]["99439"]["multiplier"] = 1.0
            st.success("✅ Conservative scenario loaded!")
            
    with col2:
        if st.button("📈 **Balanced Expansion**", help="Virginia + Florida, moderate growth", use_container_width=True):
            # Balanced scenario
            states_config["Virginia"]["active"] = True
            states_config["Florida"]["active"] = True
            for state in ["Texas", "New York", "California"]:
                states_config[state]["active"] = False
            sc["settings"]["monthly_growth"] = 0.10
            sc["settings"]["include_theoretical"] = False
            st.success("✅ Balanced scenario loaded!")
            
    with col3:
        if st.button("🚀 **Aggressive Growth**", help="All 5 states, high growth assumptions", use_container_width=True):
            # Aggressive scenario
            for state in states_config:
                states_config[state]["active"] = True
            sc["settings"]["monthly_growth"] = 0.15
            sc["settings"]["include_theoretical"] = True
            sc["rates"]["99458"]["multiplier"] = 2.0
            sc["rates"]["99439"]["multiplier"] = 1.5
            st.success("✅ Aggressive scenario loaded!")

# Step progress indicator
current_step = st.session_state.get("current_step", 1)
steps_completed = sum([
    1 if any(s["active"] for s in states_config.values()) else 0,
    1 if "multistate_df" in st.session_state else 0,
    1 if "multistate_df" in st.session_state and not st.session_state.multistate_df.empty else 0
])

st.markdown(f"""
<div class="step-indicator">
    <div class="step {'completed' if steps_completed >= 1 else 'active' if current_step == 1 else ''}">1</div>
    <div class="step {'completed' if steps_completed >= 2 else 'active' if current_step == 2 else ''}">2</div>
    <div class="step {'completed' if steps_completed >= 3 else 'active' if current_step == 3 else ''}">3</div>
</div>
<p style="text-align: center; color: {ORA_COLORS['teal']}; font-weight: 600;">
    Step 1: Choose States → Step 2: Run Model → Step 3: Analyze Results
</p>
""", unsafe_allow_html=True)

# Progress bar
progress = min(100, (steps_completed / 3) * 100)
st.markdown(f"""
<div class="progress-bar">
    <div class="progress-fill" style="width: {progress}%"></div>
</div>
""", unsafe_allow_html=True)

# Simplified sidebar
with st.sidebar:
    st.markdown('<div class="section-title">⚙️ Quick Controls</div>', unsafe_allow_html=True)
    
    st.markdown("**Timeline & Growth**")
    sc["settings"]["months"] = st.select_slider(
        "Projection Period", 
        options=[12, 24, 36, 48, 60], 
        value=sc["settings"]["months"],
        help="How many months to project forward"
    )
    
    sc["settings"]["monthly_growth"] = st.select_slider(
        "Monthly Growth Rate", 
        options=[0.05, 0.08, 0.10, 0.12, 0.15], 
        value=sc["settings"]["monthly_growth"],
        format_func=lambda x: f"{x:.1%}",
        help="How fast your patient base grows each month"
    )
    
    st.markdown("**Billing Optimization**")
    intensity = st.radio(
        "Care Intensity Level",
        ["Conservative", "Standard", "Intensive"],
        index=1,
        help="How frequently you bill additional codes per patient"
    )
    
    # Apply intensity settings
    if intensity == "Conservative":
        multipliers = {"99458": 1.0, "99439": 1.0, "99427": 1.0}
    elif intensity == "Standard":
        multipliers = {"99458": 1.35, "99439": 1.2, "99427": 1.15}
    else:  # Intensive
        multipliers = {"99458": 2.0, "99439": 1.8, "99427": 1.5}
    
    for code, mult in multipliers.items():
        if code in sc["rates"]:
            sc["rates"][code]["multiplier"] = mult
    
    st.markdown("**Advanced Options**")
    sc["settings"]["include_theoretical"] = st.checkbox(
        "Include Future Services",
        sc["settings"]["include_theoretical"],
        help="Add theoretical billing codes for advanced care management"
    )

# Main content with improved UX
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ **Step 1: Choose States**", 
    "📊 **Step 2: Run Analysis**", 
    "💰 **Step 3: View Results**", 
    "⚙️ **Advanced Settings**"
])

with tab1:
    st.markdown('<div class="section-title">🗺️ Step 1: Select Your Expansion States</div>', unsafe_allow_html=True)
    
    # Status message
    active_states = [s for s, c in states_config.items() if c["active"]]
    if not active_states:
        st.markdown(f"""
        <div class="status-message status-warning">
            <strong>⚠️ No states selected!</strong> Please choose at least one state to begin your analysis.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-message status-success">
            <strong>✅ {len(active_states)} states selected:</strong> {', '.join(active_states)}
        </div>
        """, unsafe_allow_html=True)
    
    # Simplified state selection
    st.markdown("**Choose which states to include in your expansion plan:**")
    
    for state, config in states_config.items():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            is_enabled = st.checkbox(
                state, 
                config["active"], 
                key=f"enable_{state}"
            )
            states_config[state]["active"] = is_enabled
        
        with col2:
            if is_enabled:
                # Simple inline controls
                col_a, col_b, col_c = st.columns([2, 2, 2])
                
                with col_a:
                    states_config[state]["start_month"] = st.number_input(
                        f"Launch Month", 
                        1, 60, 
                        config["start_month"], 
                        key=f"start_{state}",
                        help="When to start operations"
                    )
                
                with col_b:
                    states_config[state]["initial_patients"] = st.number_input(
                        f"Starting Patients", 
                        10, 200, 
                        config["initial_patients"],
                        key=f"patients_{state}",
                        help="Initial patient count"
                    )
                
                with col_c:
                    st.metric(
                        "GPCI Factor", 
                        f"{config['gpci']:.3f}",
                        help="Geographic payment adjustment"
                    )
                
                # State-specific guidance
                if state == "Florida":
                    st.info("🏖️ **Florida**: Large Medicare population, excellent for RPM growth")
                elif state == "Texas":
                    st.info("🤠 **Texas**: Major population centers, significant scale opportunity") 
                elif state == "New York":
                    st.info("🗽 **New York**: Higher reimbursement rates, premium market")
                elif state == "California":
                    st.info("☀️ **California**: Highest GPCI factor, tech-savvy demographics")
            else:
                st.write(f"💡 **{state}** would add {config['initial_patients']} initial patients with {config['gpci']:.1%} GPCI adjustment")

with tab2:
    st.markdown('<div class="section-title">📊 Step 2: Run Your Financial Analysis</div>', unsafe_allow_html=True)
    
    # Pre-flight checks
    active_states = [s for s, c in states_config.items() if c["active"]]
    
    if not active_states:
        st.markdown(f"""
        <div class="status-message status-warning">
            <strong>⚠️ Please go back to Step 1 and select at least one state!</strong>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Show what will be analyzed
        total_patients = sum(c["initial_patients"] for s, c in states_config.items() if c["active"])
        weighted_gpci = sum(c["initial_patients"] * c["gpci"] for s, c in states_config.items() if c["active"]) / total_patients if total_patients > 0 else 1.0
        
        st.markdown("**Your Analysis Setup:**")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("States", len(active_states))
        with col2:
            st.metric("Initial Patients", f"{total_patients:,}")
        with col3:
            st.metric("Avg GPCI", f"{weighted_gpci:.3f}")
        with col4:
            st.metric("Timeline", f"{sc['settings']['months']} months")
        
        st.markdown("**Active States:**")
        for state in active_states:
            config = states_config[state]
            st.write(f"• **{state}**: Launches Month {config['start_month']} with {config['initial_patients']} patients (GPCI: {config['gpci']:.3f})")
        
        # Big run button
        st.markdown("---")
        
        if st.button("🚀 **RUN FINANCIAL MODEL**", type="primary", use_container_width=True):
            with st.spinner("⏳ Running financial projections..."):
                try:
                    # Prepare data
                    active_states_dict = {k: v for k, v in states_config.items() if v["active"]}
                    gpci_dict = {k: v["gpci"] for k, v in active_states_dict.items()}
                    homes_dict = {k: v.get("initial_homes", 40) for k, v in active_states_dict.items()}
                    
                    # Run model
                    df = run_projection(
                        active_states_dict, 
                        gpci_dict, 
                        homes_dict, 
                        sc["rates"], 
                        sc["util"], 
                        sc["settings"]
                    )
                    
                    st.session_state.multistate_df = df
                    st.session_state.current_step = 3
                    
                    # Success message
                    st.markdown(f"""
                    <div class="status-message status-success">
                        <strong>🎉 Analysis Complete!</strong><br>
                        Generated {len(df)} data points across {len(active_states)} states over {sc['settings']['months']} months.
                        <br><strong>👉 Go to Step 3 to view your results!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Auto-refresh to show progress
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ **Error running model:** {str(e)}")
                    st.info("💡 Try selecting fewer states or reducing the timeline if you continue having issues.")

with tab3:
    st.markdown('<div class="section-title">💰 Step 3: Analyze Your Results</div>', unsafe_allow_html=True)
    
    if "multistate_df" not in st.session_state or st.session_state.multistate_df.empty:
        st.markdown(f"""
        <div class="status-message status-info">
            <strong>ℹ️ No results yet!</strong> Please complete Steps 1 and 2 to see your financial projections.
        </div>
        """, unsafe_allow_html=True)
    
    else:
        df = st.session_state.multistate_df
        
        # Key metrics dashboard
        st.markdown("### 📊 Executive Summary")
        
        final_month = df["Month"].max()
        final_patients = df[df["Month"] == final_month]["Total Patients"].sum()
        total_revenue = df["Total Revenue"].sum()
        total_ebitda = df["EBITDA"].sum()
        final_cash = df[df["Month"] == final_month]["Cash Balance"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Final Patient Count", 
                f"{final_patients:,.0f}",
                help="Total patients across all states at end of projection"
            )
        with col2:
            st.metric(
                "Cumulative Revenue", 
                f"${total_revenue:,.0f}",
                help="Total revenue generated over entire period"
            )
        with col3:
            st.metric(
                "Cumulative EBITDA", 
                f"${total_ebitda:,.0f}",
                help="Total earnings before interest, taxes, depreciation, amortization"
            )
        with col4:
            st.metric(
                "Ending Cash Position", 
                f"${final_cash:,.0f}",
                help="Cash balance at end of projection period"
            )
        
        # Revenue breakdown by billing code
        st.markdown("### 💰 Revenue by Billing Code")
        
        revenue_cols = [col for col in df.columns if col.startswith('Rev_')]
        if revenue_cols:
            monthly_revenue = df.groupby("Month")[revenue_cols].sum().reset_index()
            
            # Create stacked bar chart
            fig = go.Figure()
            
            colors = ['#200E1B', '#00B7D8', '#5F8996', '#DD3F8E', '#DF9039', 
                     '#8E44AD', '#E74C3C', '#27AE60', '#F39C12', '#3498DB', '#9B59B6', '#95A5A6']
            
            for i, col in enumerate(revenue_cols):
                code_name = col.replace('Rev_', '').replace('_', ' ')
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
                font=dict(family="Inter"),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Revenue summary table
            total_by_code = monthly_revenue[revenue_cols].sum().sort_values(ascending=False)
            
            st.markdown("**Top Revenue Sources:**")
            for i, (code, amount) in enumerate(total_by_code.head(5).items()):
                code_clean = code.replace('Rev_', '')
                percentage = (amount / total_by_code.sum()) * 100
                st.write(f"{i+1}. **{code_clean}**: ${amount:,.0f} ({percentage:.1f}%)")
        
        # State comparison
        st.markdown("### 🏛️ Performance by State")
        
        state_summary = df.groupby("State").agg({
            "Total Patients": "last",
            "Total Revenue": "sum",
            "EBITDA": "sum"
        }).round(0)
        
        st.dataframe(
            state_summary.style.format({
                'Total Patients': '{:,.0f}',
                'Total Revenue': '${:,.0f}',
                'EBITDA': '${:,.0f}'
            }),
            use_container_width=True
        )
        
        # Export button
        st.markdown("### 📁 Export Your Results")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Financial_Projections', index=False)
            state_summary.to_excel(writer, sheet_name='State_Summary')
            
            if revenue_cols:
                monthly_revenue.to_excel(writer, sheet_name='Revenue_by_Code', index=False)
        
        st.download_button(
            label="📊 **Download Complete Analysis**",
            data=output.getvalue(),
            file_name=f"ora_living_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Download Excel file with all projections and analysis"
        )

with tab4:
    st.markdown('<div class="section-title">⚙️ Advanced Settings</div>', unsafe_allow_html=True)
    
    st.info("🔧 **For Power Users**: Fine-tune billing rates, utilization, and other model parameters")
    
    # Billing rates editor
    st.markdown("**Billing Code Rates & Multipliers**")
    
    rates_df = pd.DataFrame(sc["rates"]).T.reset_index().rename(columns={"index": "Code"})
    
    # Show only the most important columns for simplicity
    display_cols = ["Code", "rate", "multiplier", "type"]
    rates_display = rates_df[display_cols].copy()
    
    edited_rates = st.data_editor(
        rates_display,
        use_container_width=True,
        column_config={
            "multiplier": st.column_config.NumberColumn(
                "Population Avg Multiplier",
                min_value=1.0,
                max_value=4.0,
                step=0.1,
                format="%.2f",
                help="Average billing frequency across patient population"
            ),
            "rate": st.column_config.NumberColumn(
                "Rate ($)",
                format="$%.2f",
                help="Reimbursement amount per billing event"
            )
        },
        hide_index=True
    )
    
    # Update rates back to session state
    for _, row in edited_rates.iterrows():
        code = row["Code"]
        if code in sc["rates"]:
            sc["rates"][code]["rate"] = row["rate"]
            sc["rates"][code]["multiplier"] = row["multiplier"]

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; color: {ORA_COLORS['teal']}; font-family: 'Inter', sans-serif;">
    <strong>Ora Living User-Friendly Financial Model</strong><br>
    <em>Providing digital healthcare solutions to safeguard our future</em><br>
    <small>Need help? Each element has hover tooltips for guidance!</small>
</div>
""", unsafe_allow_html=True)