import model
import pandas as pd

print("🎯 GROWTH MODEL AUDIT - HILL VALLEY PARTNERSHIP")
print("="*60)

# Test Hill Valley scenario
hill_valley_config = {
    "start_patients": 20,
    "max_patients": 19965,  # Target from 100 facilities × 200 patients
    "growth_rate": 0.10,
    "months": 48,
    "discharge_rate": 0.002,  # 0.2% monthly discharge rate from facilities
    "churn_rate": 0.02
}

# Run projection for Hill Valley
settings = model.default_settings()
settings.update(hill_valley_config)

results = model.run_model(
    rates=model.default_rates(),
    util=model.default_util(),
    settings=settings
)

# Check key metrics
max_patients = results['Total Patients'].max()
final_patients = results[results['Month'] == 48]['Total Patients'].iloc[0] if len(results[results['Month'] == 48]) > 0 else 0

# Find when target is reached
target_reached = None
for _, row in results.iterrows():
    if row['Total Patients'] >= 19965:
        target_reached = row['Month']
        break

print(f"\n📊 RESULTS:")
print(f"Starting patients: {hill_valley_config['start_patients']}")
print(f"Target patients: {hill_valley_config['max_patients']:,}")
print(f"Growth rate: {hill_valley_config['growth_rate']:.1%}")
print(f"Discharge rate: {hill_valley_config['discharge_rate']:.1%}")
print(f"Churn rate: {hill_valley_config['churn_rate']:.1%}")
print(f"\n🏁 OUTCOMES:")
print(f"Max patients reached: {max_patients:,.0f}")
print(f"Patients at month 48: {final_patients:,.0f}")

if target_reached:
    print(f"✅ Target of 19,965 reached at month {target_reached}")
else:
    print(f"❌ Target NOT reached! Max was {max_patients:,.0f}")
    
# Check growth phases
if 'Phase' in results.columns:
    phases = results.groupby('Phase')['Month'].agg(['min', 'max'])
    print(f"\n📈 GROWTH PHASES:")
    for phase, row in phases.iterrows():
        print(f"  {phase}: Months {row['min']}-{row['max']}")

# Revenue check at target
if target_reached:
    target_month_data = results[results['Month'] == target_reached].iloc[0]
    revenue_per_patient = target_month_data['Total Revenue'] / target_month_data['Total Patients']
    print(f"\n💰 At target (month {target_reached}):")
    print(f"  Revenue per patient: ${revenue_per_patient:.2f}")
    print(f"  Total revenue: ${target_month_data['Total Revenue']:,.0f}")
    print(f"  EBITDA: ${target_month_data['EBITDA']:,.0f}")
    print(f"  EBITDA margin: {(target_month_data['EBITDA']/target_month_data['Total Revenue']*100):.1f}%")