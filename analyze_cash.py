import model
import pandas as pd

# Test Aggressive scenario month by month
settings = model.default_settings()
settings.update({
    'hill_valley_monthly_discharges': 1100,
    'initial_capture_rate': 0.70,
    'target_capture_rate': 0.95,
    'growth_multiplier': 1.6,
    'monthly_attrition': 0.025,
    'months': 48,  # Extended to match On Timeline duration
    'max_patients': 19965
})

rates = model.default_rates()
util = model.default_util()

df_aggressive = model.run_model(rates, util, settings)

# Test On Timeline scenario
settings2 = model.default_settings()
settings2.update({
    'hill_valley_monthly_discharges': 850,
    'initial_capture_rate': 0.60,
    'target_capture_rate': 0.90,
    'growth_multiplier': 1.4,
    'monthly_attrition': 0.03,
    'months': 48,
    'max_patients': 19965
})

df_timeline = model.run_model(rates, util, settings2)

print("Aggressive (Extended to 48 months):")
print(f"  Max patients: {df_aggressive['Total Patients'].max():,.0f}")
print(f"  Final cash @ 48mo: ${df_aggressive['Cash Balance'].iloc[-1]:,.0f}")
print(f"  Cash @ 36mo: ${df_aggressive['Cash Balance'].iloc[35]:,.0f}")

print("\nOn Timeline (48 months):")
print(f"  Max patients: {df_timeline['Total Patients'].max():,.0f}")
print(f"  Final cash @ 48mo: ${df_timeline['Cash Balance'].iloc[-1]:,.0f}")

# Compare month 29 (when aggressive hits target)
print(f"\nAt Month 29 (Aggressive hits target):")
print(f"  Aggressive patients: {df_aggressive['Total Patients'].iloc[28]:,.0f}")
print(f"  Aggressive cash: ${df_aggressive['Cash Balance'].iloc[28]:,.0f}")
print(f"  On Timeline patients: {df_timeline['Total Patients'].iloc[28]:,.0f}")
print(f"  On Timeline cash: ${df_timeline['Cash Balance'].iloc[28]:,.0f}")

# Check monthly cash flow
print("\nMonthly EBITDA comparison (months 25-30):")
for m in range(24, 30):
    print(f"Month {m+1}: Aggressive=${df_aggressive['EBITDA'].iloc[m]:,.0f}, On Timeline=${df_timeline['EBITDA'].iloc[m]:,.0f}")