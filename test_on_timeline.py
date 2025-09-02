import model

# Test On Timeline scenario exactly as configured in app
settings = model.default_settings()
settings.update({
    'hill_valley_monthly_discharges': 900,
    'initial_capture_rate': 0.60,
    'target_capture_rate': 0.95,
    'growth_multiplier': 1.4,
    'monthly_attrition': 0.03,
    'months': 60,
    'max_patients': 19965
})

rates = model.default_rates()
util = model.default_util()

df = model.run_model(rates, util, settings)

# Find when target is reached
target_month = None
for idx, row in df.iterrows():
    if row['Total Patients'] >= 19956:  # Using the actual calculated target
        target_month = row['Month']
        break

max_patients = df['Total Patients'].max()
print(f"On Timeline Scenario Results:")
print(f"  Max patients reached: {max_patients:,.0f}")
print(f"  Target (19,956) reached at: Month {target_month}" if target_month else "  Target NOT reached")

# Show patient growth month by month around target
print("\nPatient growth trajectory:")
for m in range(30, 45):
    if m < len(df):
        print(f"  Month {m}: {df.iloc[m-1]['Total Patients']:,.0f} patients")