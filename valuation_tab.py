import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ora Living Brand Colors
ORA_COLORS = {
    'primary_dark': '#200E1B',
    'primary_cyan': '#00B7D8', 
    'teal': '#5F8996',
    'magenta': '#DD3F8E',
    'orange': '#DF9039',
}

def show_valuation_analysis(df):
    """
    Comprehensive valuation analysis for Ora Living including:
    - DCF Analysis
    - Comparable Company Analysis  
    - Healthcare Tech Multiples
    - Sensitivity Analysis
    """
    
    st.markdown('<div class="section-header">💰 Valuation Analysis</div>', unsafe_allow_html=True)
    
    # Valuation tabs
    val_tab1, val_tab2, val_tab3, val_tab4 = st.tabs([
        "📊 DCF Analysis", 
        "🏢 Comparable Companies", 
        "🩺 HealthTech Multiples",
        "📈 Sensitivity Analysis"
    ])
    
    with val_tab1:
        show_dcf_analysis(df)
        
    with val_tab2:
        show_comparable_analysis()
        
    with val_tab3:
        show_healthtech_multiples()
        
    with val_tab4:
        show_sensitivity_analysis(df)

def show_dcf_analysis(df):
    """Discounted Cash Flow valuation analysis"""
    
    st.markdown("### 📊 Discounted Cash Flow (DCF) Valuation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**DCF Assumptions**")
        
        # DCF parameters
        wacc = st.slider("WACC (Weighted Average Cost of Capital)", 8.0, 15.0, 12.0, 0.5) / 100
        terminal_growth = st.slider("Terminal Growth Rate", 2.0, 4.0, 2.5, 0.1) / 100
        projection_years = st.slider("Explicit Forecast Period (Years)", 5, 10, 5)
        
        # Risk adjustments for early-stage healthtech
        st.markdown("**Risk Adjustments**")
        execution_risk = st.slider("Execution Risk Discount", 0.0, 30.0, 15.0, 1.0) / 100
        regulatory_risk = st.slider("Regulatory Risk Discount", 0.0, 20.0, 10.0, 1.0) / 100
        
    with col2:
        st.markdown("**Free Cash Flow Projections**")
        
        # Extract FCF from model
        annual_data = []
        for year in range(1, projection_years + 1):
            year_months = [i for i in range((year-1)*12 + 1, year*12 + 1) if i <= len(df)]
            if year_months:
                year_df = df[df['Month'].isin(year_months)]
                fcf = year_df['Free Cash Flow'].sum()
                revenue = year_df['Total Revenue'].sum()
                ebitda = year_df['EBITDA'].sum()
                annual_data.append({
                    'Year': year,
                    'Revenue': revenue,
                    'EBITDA': ebitda,
                    'Free Cash Flow': fcf
                })
        
        fcf_df = pd.DataFrame(annual_data)
        
        # Display FCF projections
        for _, row in fcf_df.iterrows():
            st.write(f"Year {row['Year']}: ${row['Free Cash Flow']:,.0f}")
    
    # DCF Calculation
    if len(fcf_df) > 0:
        st.markdown("### 💹 Valuation Results")
        
        # Present value of explicit period
        pv_explicit = 0
        for _, row in fcf_df.iterrows():
            pv_year = row['Free Cash Flow'] / ((1 + wacc) ** row['Year'])
            pv_explicit += pv_year
        
        # Terminal value
        final_year_fcf = fcf_df['Free Cash Flow'].iloc[-1]
        terminal_value = (final_year_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1 + wacc) ** projection_years)
        
        # Enterprise value
        enterprise_value = pv_explicit + pv_terminal
        
        # Apply risk discounts
        risk_adjusted_value = enterprise_value * (1 - execution_risk) * (1 - regulatory_risk)
        
        # Display results
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PV of Explicit Period", f"${pv_explicit:,.0f}")
        with col2:
            st.metric("PV of Terminal Value", f"${pv_terminal:,.0f}")
        with col3:
            st.metric("Enterprise Value", f"${enterprise_value:,.0f}")
        with col4:
            st.metric("Risk-Adjusted Value", f"${risk_adjusted_value:,.0f}")
        
        # Valuation bridge chart
        bridge_data = {
            'Component': ['PV Explicit', 'PV Terminal', 'Execution Risk', 'Regulatory Risk', 'Final Value'],
            'Value': [pv_explicit, pv_terminal, -enterprise_value*execution_risk, -enterprise_value*regulatory_risk, 0],
            'Cumulative': [pv_explicit, pv_explicit + pv_terminal, enterprise_value - enterprise_value*execution_risk, 
                          risk_adjusted_value, risk_adjusted_value]
        }
        bridge_df = pd.DataFrame(bridge_data)
        
        fig = go.Figure()
        
        # Add waterfall chart
        for i, row in bridge_df.iterrows():
            color = ORA_COLORS['primary_cyan'] if row['Value'] > 0 else ORA_COLORS['magenta']
            if i == len(bridge_df) - 1:
                color = ORA_COLORS['teal']
            
            fig.add_trace(go.Bar(
                x=[row['Component']],
                y=[row['Cumulative']],
                name=row['Component'],
                marker_color=color,
                showlegend=False
            ))
        
        fig.update_layout(
            title="DCF Valuation Bridge",
            yaxis_title="Valuation ($)",
            font=dict(family="Inter"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_comparable_analysis():
    """Comparable company analysis for RPM/CCM companies"""
    
    st.markdown("### 🏢 Comparable Company Analysis")
    
    # RPM/CCM and Relevant Healthcare Tech Companies
    comp_data = {
        'Company': [
            'CareSimple (Private)', 'Impilo (Private)', 'RPM Health', 'CarePrecise',
            'Teladoc Health', 'American Well', 'MDLive (Evernorth)', 'Doxy.me',
            'Current Health', 'Philips Healthcare'
        ],
        'Market Cap ($M)': [150, 50, 80, 120, 2400, 800, 750, 300, 400, 25000],
        'Revenue ($M)': [25, 8, 15, 20, 2650, 744, 500, 45, 80, 8500],
        'Revenue Multiple': [6.0, 6.3, 5.3, 6.0, 0.9, 1.1, 1.5, 6.7, 5.0, 2.9],
        'EBITDA Margin (%)': [35.0, 40.0, 30.0, 32.0, 2.1, -15.2, 8.0, 25.0, 15.0, 18.5],
        'Category': [
            'RPM Platform', 'RPM Platform', 'RPM/CCM Services', 'RPM/CCM Services',
            'Telehealth Platform', 'Telehealth Platform', 'Telehealth Services', 'Telehealth Platform',
            'RPM/IoT Health', 'Healthcare Technology'
        ]
    }
    
    comp_df = pd.DataFrame(comp_data)
    
    # Display comparable companies
    st.dataframe(comp_df.style.format({
        'Market Cap ($B)': '{:.1f}',
        'Revenue ($M)': '{:.0f}',
        'Revenue Multiple': '{:.1f}x',
        'EBITDA Margin (%)': '{:.1f}%'
    }), use_container_width=True)
    
    # Analysis by category
    st.markdown("### 📊 Multiples Analysis by Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue multiples by category
        category_stats = comp_df.groupby('Category').agg({
            'Revenue Multiple': ['mean', 'median', 'min', 'max']
        }).round(1)
        category_stats.columns = ['Mean', 'Median', 'Min', 'Max']
        
        st.markdown("**Revenue Multiples by Category**")
        st.dataframe(category_stats, use_container_width=True)
        
    with col2:
        # EBITDA margins by category
        margin_stats = comp_df.groupby('Category').agg({
            'EBITDA Margin (%)': ['mean', 'median']
        }).round(1)
        margin_stats.columns = ['Mean Margin', 'Median Margin']
        
        st.markdown("**EBITDA Margins by Category**")
        st.dataframe(margin_stats, use_container_width=True)
    
    # Ora Living positioning
    st.markdown("### 🎯 Ora Living Positioning")
    
    # Calculate implied valuation ranges for Ora Living
    total_revenue = 3448107  # From our model (60 month total)
    annual_revenue = total_revenue / 5  # Average annual revenue
    
    telehealth_multiple = comp_df[comp_df['Category'] == 'Telehealth Platform']['Revenue Multiple'].mean()
    digital_health_multiple = comp_df[comp_df['Category'] == 'Digital Health']['Revenue Multiple'].mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        telehealth_valuation = annual_revenue * telehealth_multiple
        st.metric(
            "Telehealth Platform Multiple",
            f"${telehealth_valuation:,.0f}",
            f"{telehealth_multiple:.1f}x revenue"
        )
    
    with col2:
        digital_health_valuation = annual_revenue * digital_health_multiple
        st.metric(
            "Digital Health Multiple", 
            f"${digital_health_valuation:,.0f}",
            f"{digital_health_multiple:.1f}x revenue"
        )
        
    with col3:
        blended_multiple = (telehealth_multiple + digital_health_multiple) / 2
        blended_valuation = annual_revenue * blended_multiple
        st.metric(
            "Blended Multiple",
            f"${blended_valuation:,.0f}",
            f"{blended_multiple:.1f}x revenue"
        )

def show_healthtech_multiples():
    """Healthcare technology specific valuation multiples"""
    
    st.markdown("### 🩺 Healthcare Technology Valuation Multiples")
    
    # Healthcare tech subsector analysis
    subsector_data = {
        'Subsector': [
            'Remote Patient Monitoring',
            'Chronic Care Management', 
            'Digital Therapeutics',
            'Health Analytics/AI',
            'Telehealth Platforms',
            'Healthcare SaaS',
            'Medical Devices (Connected)',
            'Health Data/Interoperability'
        ],
        'Revenue Multiple Range': [
            '3-8x', '4-10x', '5-15x', '8-20x',
            '1-6x', '10-25x', '6-12x', '5-12x'
        ],
        'Typical EBITDA Margin': [
            '20-40%', '25-45%', '10-30%', '15-35%',
            '-10-20%', '25-50%', '30-50%', '20-40%'
        ],
        'Growth Rate (Annual)': [
            '25-50%', '30-60%', '40-80%', '50-100%',
            '20-40%', '30-60%', '15-30%', '25-45%'
        ],
        'Market Maturity': [
            'Growth', 'Growth', 'Early', 'Early',
            'Mature', 'Growth', 'Mature', 'Growth'
        ]
    }
    
    subsector_df = pd.DataFrame(subsector_data)
    st.dataframe(subsector_df, use_container_width=True, hide_index=True)
    
    # Ora Living specific analysis
    st.markdown("### 🎯 Ora Living Valuation Framework")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Ora Living Business Model Positioning:**
        - **Primary**: Remote Patient Monitoring (RPM)
        - **Secondary**: Chronic Care Management (CCM)
        - **Technology**: AI-Enhanced Healthcare Analytics
        - **Market Stage**: Growth phase with strong unit economics
        """)
        
        # Blended multiple calculation
        rpm_multiple_low, rpm_multiple_high = 3, 8
        ccm_multiple_low, ccm_multiple_high = 4, 10
        
        # Weight: 60% RPM, 40% CCM
        blended_low = rpm_multiple_low * 0.6 + ccm_multiple_low * 0.4
        blended_high = rpm_multiple_high * 0.6 + ccm_multiple_high * 0.4
        
        st.markdown(f"""
        **Blended Revenue Multiple Range:**
        - **Conservative**: {blended_low:.1f}x
        - **Aggressive**: {blended_high:.1f}x
        - **Target Range**: {blended_low:.1f}x - {blended_high:.1f}x
        """)
    
    with col2:
        st.markdown("""
        **Valuation Premium Factors:**
        ✅ **AI-Enhanced Platform** (+10-20%)
        ✅ **Proven Unit Economics** (+15-25%) 
        ✅ **Multi-State Scalability** (+10-15%)
        ✅ **Strong EBITDA Margins** (+15-20%)
        ✅ **Recurring Revenue Model** (+10-15%)
        
        **Valuation Discount Factors:**
        ❌ **Early Stage/Execution Risk** (-15-25%)
        ❌ **Regulatory Dependency** (-10-15%)
        ❌ **Competition Risk** (-10-15%)
        """)
        
        # Net premium/discount
        net_adjustment = st.slider(
            "Net Valuation Adjustment",
            -30.0, 30.0, 5.0, 2.5,
            help="Net adjustment for premium/discount factors"
        )
        
        adjusted_low = blended_low * (1 + net_adjustment/100)
        adjusted_high = blended_high * (1 + net_adjustment/100)
        
        st.markdown(f"""
        **Risk-Adjusted Multiple:**
        - **Range**: {adjusted_low:.1f}x - {adjusted_high:.1f}x
        - **Adjustment**: {net_adjustment:+.1f}%
        """)

def show_sensitivity_analysis(df):
    """Sensitivity analysis for key valuation drivers"""
    
    st.markdown("### 📈 Valuation Sensitivity Analysis")
    
    # Key sensitivity parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Sensitivity Variables**")
        
        # Base case assumptions
        base_revenue_multiple = st.slider("Base Revenue Multiple", 3.0, 15.0, 6.0, 0.5)
        base_annual_revenue = 3448107 / 5  # 5-year average
        
        # Sensitivity ranges
        revenue_growth_range = st.slider("Revenue Growth Range (+/-)", 10, 50, 25)
        multiple_range = st.slider("Multiple Range (+/-)", 1.0, 5.0, 2.0, 0.5)
        
    with col2:
        st.markdown("**Scenario Analysis**")
        
        scenarios = {
            'Bear Case': {
                'revenue_factor': 1 - revenue_growth_range/100,
                'multiple_factor': base_revenue_multiple - multiple_range,
                'description': 'Conservative growth, market compression'
            },
            'Base Case': {
                'revenue_factor': 1.0,
                'multiple_factor': base_revenue_multiple,
                'description': 'Current model projections'
            },
            'Bull Case': {
                'revenue_factor': 1 + revenue_growth_range/100,
                'multiple_factor': base_revenue_multiple + multiple_range,
                'description': 'Accelerated growth, premium multiple'
            }
        }
        
        scenario_results = []
        for scenario, params in scenarios.items():
            adjusted_revenue = base_annual_revenue * params['revenue_factor']
            valuation = adjusted_revenue * params['multiple_factor']
            scenario_results.append({
                'Scenario': scenario,
                'Annual Revenue': f"${adjusted_revenue:,.0f}",
                'Multiple': f"{params['multiple_factor']:.1f}x",
                'Valuation': f"${valuation:,.0f}",
                'Description': params['description']
            })
        
        scenario_df = pd.DataFrame(scenario_results)
        st.dataframe(scenario_df, use_container_width=True, hide_index=True)
    
    # Monte Carlo simulation parameters
    st.markdown("### 🎲 Monte Carlo Valuation Simulation")
    
    if st.button("Run Monte Carlo Simulation (1000 iterations)"):
        # Simulation parameters
        n_simulations = 1000
        
        # Random variables
        np.random.seed(42)
        revenue_multipliers = np.random.normal(1.0, 0.25, n_simulations)  # 25% std dev
        multiples = np.random.normal(base_revenue_multiple, 1.5, n_simulations)  # 1.5x std dev
        
        # Calculate valuations
        valuations = []
        for i in range(n_simulations):
            sim_revenue = base_annual_revenue * max(0.3, revenue_multipliers[i])  # Floor at 30%
            sim_multiple = max(1.0, multiples[i])  # Floor at 1x
            valuation = sim_revenue * sim_multiple
            valuations.append(valuation)
        
        valuations = np.array(valuations)
        
        # Results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Mean Valuation", f"${np.mean(valuations):,.0f}")
            st.metric("Median Valuation", f"${np.median(valuations):,.0f}")
            
        with col2:
            st.metric("90th Percentile", f"${np.percentile(valuations, 90):,.0f}")
            st.metric("10th Percentile", f"${np.percentile(valuations, 10):,.0f}")
            
        with col3:
            confidence_90 = np.percentile(valuations, [5, 95])
            st.metric("90% Confidence Range", 
                     f"${confidence_90[0]:,.0f} - ${confidence_90[1]:,.0f}")
        
        # Distribution plot
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=valuations/1000000,  # Convert to millions
            nbinsx=50,
            name='Valuation Distribution',
            marker_color=ORA_COLORS['primary_cyan']
        ))
        
        fig.update_layout(
            title='Monte Carlo Valuation Distribution',
            xaxis_title='Valuation ($M)',
            yaxis_title='Frequency',
            font=dict(family="Inter"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key statistics
        st.markdown("**Distribution Statistics:**")
        st.write(f"- **Standard Deviation**: ${np.std(valuations):,.0f}")
        st.write(f"- **Coefficient of Variation**: {np.std(valuations)/np.mean(valuations):.1%}")
        st.write(f"- **Probability > $5M**: {np.sum(valuations > 5000000)/len(valuations):.1%}")
        st.write(f"- **Probability > $10M**: {np.sum(valuations > 10000000)/len(valuations):.1%}")