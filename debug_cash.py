import model

# Test exactly what the app is running
settings = model.default_settings()

# Aggressive scenario as set by the button
settings['hill_valley_monthly_discharges'] = 1100
settings['initial_capture_rate'] = 0.70
settings['target_capture_rate'] = 0.95
settings['growth_multiplier'] = 1.6
settings['monthly_attrition'] = 0.025
settings['months'] = 60
settings['max_patients'] = 19965

rates = model.default_rates()
util = model.default_util()

df = model.run_model(rates, util, settings)

print("AGGRESSIVE SCENARIO - What you should see in the UI:")
print("=" * 60)
print(f"Month 60 Cash Balance: ${df['Cash Balance'].iloc[-1]:,.0f}")
print(f"Month 48 Cash Balance: ${df['Cash Balance'].iloc[47]:,.0f}")
print(f"Month 36 Cash Balance: ${df['Cash Balance'].iloc[35]:,.0f}")
print(f"Max Patients: {df['Total Patients'].max():,.0f}")

# Find target month
target_month = None
for idx, row in df.iterrows():
    if row['Total Patients'] >= 19956:
        target_month = row['Month']
        break

print(f"Target reached: Month {target_month}")

# Check cumulative EBITDA
cumulative_ebitda = df['EBITDA'].sum()
print(f"Cumulative EBITDA: ${cumulative_ebitda:,.0f}")

# Show last few months of cash
print("\nLast 5 months of cash balance:")
for i in range(55, 60):
    print(f"  Month {i+1}: ${df['Cash Balance'].iloc[i]:,.0f}")