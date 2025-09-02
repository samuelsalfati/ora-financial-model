import model

# Test just Virginia with simple settings
states = {"Virginia": {"start_month": 1, "initial_patients": 10000, "active": True}}
gpci = {"Virginia": 1.0}
homes = {"Virginia": 40}

rates = model.default_rates()
util = model.default_util()
settings = model.default_settings()
settings["initial_patients"] = 10000
settings["months"] = 30

df = model.run_projection(states, gpci, homes, rates, util, settings)

print("Month-by-month around month 24:")
print("Month | Patients | Revenue | EBITDA | Cash Balance")
for _, row in df[(df['Month'] >= 20) & (df['Month'] <= 28)].iterrows():
    print(f"{row['Month']:5d} | {row['Total Patients']:8.0f} | {row['Total Revenue']:10.0f} | {row['EBITDA']:10.0f} | {row['Cash Balance']:15.0f}")

# Check for any sudden jumps
month_23 = df[df['Month'] == 23].iloc[0] if len(df[df['Month'] == 23]) > 0 else None
month_24 = df[df['Month'] == 24].iloc[0] if len(df[df['Month'] == 24]) > 0 else None

if month_23 is not None and month_24 is not None:
    print(f"\nJump from Month 23 to 24:")
    print(f"Patients: {month_23['Total Patients']:.0f} → {month_24['Total Patients']:.0f}")
    print(f"Revenue: ${month_23['Total Revenue']:,.0f} → ${month_24['Total Revenue']:,.0f}")
    print(f"Cash: ${month_23['Cash Balance']:,.0f} → ${month_24['Cash Balance']:,.0f}")