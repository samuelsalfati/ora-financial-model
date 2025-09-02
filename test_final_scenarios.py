import model

scenarios = {
    'Conservative': {
        'hill_valley_monthly_discharges': 700,
        'initial_capture_rate': 0.50,
        'target_capture_rate': 0.80,  # This is 80% of base, not 1.80
        'growth_multiplier': 1.2,
        'monthly_attrition': 0.03,
        'months': 60,
        'max_patients': 19965
    },
    'On Timeline': {
        'hill_valley_monthly_discharges': 900,
        'initial_capture_rate': 0.60,
        'target_capture_rate': 0.95,  # This is 95% of base, not 1.95
        'growth_multiplier': 1.4,
        'monthly_attrition': 0.03,
        'months': 60,
        'max_patients': 19965
    },
    'Aggressive': {
        'hill_valley_monthly_discharges': 1100,
        'initial_capture_rate': 0.70,
        'target_capture_rate': 0.95,  # This is 95% of base, not 1.95
        'growth_multiplier': 1.6,
        'monthly_attrition': 0.025,
        'months': 60,
        'max_patients': 19965
    }
}

rates = model.default_rates()
util = model.default_util()

print("FINAL SCENARIO TEST RESULTS")
print("=" * 70)
print(f"{'Scenario':<15} {'Target Month':<15} {'Final Cash':<20} {'Max Patients':<15}")
print("-" * 70)

for name, params in scenarios.items():
    settings = model.default_settings()
    settings.update(params)
    
    df = model.run_model(rates, util, settings)
    
    max_patients = df['Total Patients'].max()
    final_cash = df['Cash Balance'].iloc[-1]
    
    # Find when target is reached
    target_month = None
    for idx, row in df.iterrows():
        if row['Total Patients'] >= 19956:
            target_month = row['Month']
            break
    
    target_str = f"Month {target_month}" if target_month else "Not reached"
    
    print(f"{name:<15} {target_str:<15} ${final_cash:>18,.0f} {max_patients:>14,.0f}")

print("=" * 70)
print("\nExpected Results:")
print("- Aggressive should reach target earliest (Month ~29) with highest cash")
print("- On Timeline should reach target around Month 38-40 with medium cash")
print("- Conservative should struggle to reach target with lowest cash")