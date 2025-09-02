import model
import pandas as pd

# Test each scenario configuration
scenarios = {
    'Conservative (5Y)': {
        'hill_valley_monthly_discharges': 700,
        'initial_capture_rate': 0.50,
        'target_capture_rate': 0.80,
        'growth_multiplier': 1.2,
        'monthly_attrition': 0.03,
        'months': 60,
        'max_patients': 19965
    },
    'On Timeline (4Y)': {
        'hill_valley_monthly_discharges': 850,
        'initial_capture_rate': 0.60,
        'target_capture_rate': 0.90,
        'growth_multiplier': 1.4,
        'monthly_attrition': 0.03,
        'months': 48,
        'max_patients': 19965
    },
    'Aggressive (3Y)': {
        'hill_valley_monthly_discharges': 1100,
        'initial_capture_rate': 0.70,
        'target_capture_rate': 0.95,
        'growth_multiplier': 1.6,
        'monthly_attrition': 0.025,
        'months': 36,
        'max_patients': 19965
    }
}

rates = model.default_rates()
util = model.default_util()

for name, params in scenarios.items():
    settings = model.default_settings()
    settings.update(params)
    
    df = model.run_model(rates, util, settings)
    
    max_patients = df['Total Patients'].max()
    final_cash = df['Cash Balance'].iloc[-1]
    target_month = df[df['Total Patients'] >= 19965]['Month'].min() if any(df['Total Patients'] >= 19965) else None
    
    print(f'\n{name}:')
    print(f'  Max patients: {max_patients:,.0f}')
    print(f'  Target reached: Month {target_month}' if pd.notna(target_month) else '  Target NOT reached')
    print(f'  Final cash: ${final_cash:,.0f}')
    print(f'  Months: {params["months"]}')