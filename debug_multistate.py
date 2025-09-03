import model
import pandas as pd

# Debug exactly what happens with multi-state
settings = model.default_settings()
settings['months'] = 48

print("MULTI-STATE DEBUGGING")
print("=" * 80)

# Test 1: Virginia only
print("\n1. VIRGINIA ONLY:")
states_va = {"Virginia": {"start_month": 1, "initial_patients": 100, "active": True}}
df_va = model.run_projection(
    states_va,
    {"Virginia": 1.00},
    {"Virginia": 100},
    model.default_rates(),
    model.default_util(),
    settings
)

# Check specific months
for month in [1, 12, 24, 36, 48]:
    row = df_va[df_va['Month'] == month].iloc[0] if len(df_va[df_va['Month'] == month]) > 0 else None
    if row is not None:
        print(f"  Month {month:2}: Patients={row['Total Patients']:6.0f}, Revenue=${row['Total Revenue']:10.0f}, Costs=${row['Total Costs']:10.0f}")

# Test 2: Florida only (to see if it grows)
print("\n2. FLORIDA ONLY:")
states_fl = {"Florida": {"start_month": 1, "initial_patients": 100, "active": True}}
df_fl = model.run_projection(
    states_fl,
    {"Florida": 1.05},
    {"Florida": 60},
    model.default_rates(),
    model.default_util(),
    settings
)

for month in [1, 12, 24, 36, 48]:
    row = df_fl[df_fl['Month'] == month].iloc[0] if len(df_fl[df_fl['Month'] == month]) > 0 else None
    if row is not None:
        print(f"  Month {month:2}: Patients={row['Total Patients']:6.0f}, Revenue=${row['Total Revenue']:10.0f}, Costs=${row['Total Costs']:10.0f}")

# Test 3: Both states together
print("\n3. VIRGINIA + FLORIDA TOGETHER:")
states_both = {
    "Virginia": {"start_month": 1, "initial_patients": 100, "active": True},
    "Florida": {"start_month": 1, "initial_patients": 100, "active": True}
}
df_both = model.run_projection(
    states_both,
    {"Virginia": 1.00, "Florida": 1.05},
    {"Virginia": 100, "Florida": 60},
    model.default_rates(),
    model.default_util(),
    settings
)

for month in [1, 12, 24, 36, 48]:
    row = df_both[df_both['Month'] == month].iloc[0] if len(df_both[df_both['Month'] == month]) > 0 else None
    if row is not None:
        print(f"  Month {month:2}: Patients={row['Total Patients']:6.0f}, Revenue=${row['Total Revenue']:10.0f}, Costs=${row['Total Costs']:10.0f}")

# Check state-by-state breakdown
print("\n4. STATE BREAKDOWN AT MONTH 48:")
print("  Looking for columns:", [col for col in df_both.columns if 'Virginia' in col or 'Florida' in col])

# The issue analysis
print("\n" + "=" * 80)
print("EXPECTED BEHAVIOR:")
print("- Florida alone should grow to ~20K patients (same as Virginia)")
print("- Virginia + Florida should have ~40K total patients")
print("- Costs per patient should DECREASE with scale")
print("- EBITDA margin should INCREASE with scale")

print("\nACTUAL BEHAVIOR:")
va_final = df_va[df_va['Month'] == 48].iloc[0]
fl_final = df_fl[df_fl['Month'] == 48].iloc[0]
both_final = df_both[df_both['Month'] == 48].iloc[0]

print(f"- Virginia alone: {va_final['Total Patients']:.0f} patients")
print(f"- Florida alone: {fl_final['Total Patients']:.0f} patients")
print(f"- Both together: {both_final['Total Patients']:.0f} patients (should be ~40K!)")

if both_final['Total Patients'] < (va_final['Total Patients'] + fl_final['Total Patients']) * 0.9:
    print("\n❌ PROBLEM: States aren't growing independently!")
    print("   Florida is being capped or not growing properly when combined with Virginia")