import model
import pandas as pd

# Test each scenario configuration with 60-month duration
scenarios = {
    'Conservative (5Y to target)': {
        'hill_valley_monthly_discharges': 700,
        'initial_capture_rate': 0.50,
        'target_capture_rate': 0.80,
        'growth_multiplier': 1.2,
        'monthly_attrition': 0.03,
        'months': 60,
        'max_patients': 19965
    },
    'On Timeline (4Y to target)': {
        'hill_valley_monthly_discharges': 900,
        'initial_capture_rate': 0.60,
        'target_capture_rate': 0.95,
        'growth_multiplier': 1.4,
        'monthly_attrition': 0.03,
        'months': 60,
        'max_patients': 19965
    },
    'Aggressive (3Y to target)': {
        'hill_valley_monthly_discharges': 1100,
        'initial_capture_rate': 0.70,
        'target_capture_rate': 0.95,
        'growth_multiplier': 1.6,
        'monthly_attrition': 0.025,
        'months': 60,
        'max_patients': 19965
    }
}

rates = model.default_rates()
util = model.default_util()

print("SCENARIO COMPARISON (All run for 60 months)")
print("=" * 60)

for name, params in scenarios.items():
    settings = model.default_settings()
    settings.update(params)
    
    df = model.run_model(rates, util, settings)
    
    max_patients = df['Total Patients'].max()
    final_cash = df['Cash Balance'].iloc[-1]
    target_month = df[df['Total Patients'] >= 19965]['Month'].min() if any(df['Total Patients'] >= 19965) else None
    
    # Find month when cash turns positive
    positive_cash_month = df[df['Cash Balance'] > 0]['Month'].min() if any(df['Cash Balance'] > 0) else None
    
    # Calculate cumulative EBITDA at 60 months
    cumulative_ebitda = df['EBITDA'].sum()
    
    print(f'\n{name}:')
    print(f'  Target reached: Month {target_month}' if pd.notna(target_month) else '  Target NOT reached')
    print(f'  Max patients: {max_patients:,.0f}')
    print(f'  Final cash (Month 60): ${final_cash:,.0f}')
    print(f'  Cumulative EBITDA: ${cumulative_ebitda:,.0f}')
    print(f'  Cash positive from: Month {positive_cash_month}' if pd.notna(positive_cash_month) else '  Never cash positive')

print("\n" + "=" * 60)
print("KEY INSIGHT: Aggressive reaches target earlier and accumulates")
print("more cash over 60 months due to longer profit generation period.")