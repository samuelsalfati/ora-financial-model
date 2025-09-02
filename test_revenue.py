import model

# Simple test of Virginia only with basic settings
states = {"Virginia": {"start_month": 1, "initial_patients": 10000, "active": True}}
gpci = {"Virginia": 1.0}
homes = {"Virginia": 40}

rates = model.default_rates()
util = model.default_util()
settings = model.default_settings()

# Override with simple settings
settings["initial_patients"] = 10000
settings["monthly_growth"] = 0.08  # 8% growth
settings["monthly_attrition"] = 0.015  # 1.5% attrition
settings["months"] = 12

print("Testing revenue progression with Virginia only:")
print("Growth: 8% monthly, Attrition: 1.5% monthly, Net: 6.5% monthly")
print("Starting patients: 10,000")
print()

df = model.run_projection(states, gpci, homes, rates, util, settings)

# Model should now allow growth from current patient base
print()

# Show first 12 months
print("Month | Patients | Revenue | EBITDA")
for _, row in df.head(12).iterrows():
    print(f"{row['Month']:5d} | {row['Total Patients']:8.0f} | {row['Total Revenue']:8.0f} | {row['EBITDA']:8.0f}")

# Check if revenue is going up or down
if len(df) >= 2:
    first_revenue = df.iloc[0]['Total Revenue']
    last_revenue = df.iloc[-1]['Total Revenue']
    print(f"\nRevenue change: ${first_revenue:,.0f} → ${last_revenue:,.0f}")
    if last_revenue > first_revenue:
        print("✅ Revenue is increasing")
    else:
        print("❌ Revenue is decreasing")