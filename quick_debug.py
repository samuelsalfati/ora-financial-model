import model

# Simple test - Virginia only, 12 months
states = {"Virginia": {"start_month": 1, "initial_patients": 10000, "active": True}}
gpci = {"Virginia": 1.0}
homes = {"Virginia": 40}

rates = model.default_rates()
util = model.default_util()
settings = model.default_settings()
settings["initial_patients"] = 10000
settings["months"] = 15

df = model.run_projection(states, gpci, homes, rates, util, settings)

print("DEBUGGING MONTH 8-12:")
print("Month | Patients | Revenue  | EBITDA   | Growth")
for month in range(8, 13):
    row = df[df['Month'] == month]
    if len(row) > 0:
        r = row.iloc[0]
        prev_row = df[df['Month'] == month-1]
        if len(prev_row) > 0:
            patient_growth = r['Total Patients'] - prev_row.iloc[0]['Total Patients']
        else:
            patient_growth = 0
        print(f"{month:5d} | {r['Total Patients']:8.0f} | {r['Total Revenue']:8.0f} | {r['EBITDA']:8.0f} | {patient_growth:+6.0f}")

# Check if growth rate is actually being applied
print(f"\nModel settings:")
print(f"Growth: {settings['monthly_growth']*100:.1f}%")
print(f"Attrition: {settings['monthly_attrition']*100:.1f}%")
print(f"Net: {(settings['monthly_growth'] - settings['monthly_attrition'])*100:.2f}%")