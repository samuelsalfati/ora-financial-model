import model
import pandas as pd

# Test both states with detailed output
settings = model.default_settings()
settings['months'] = 6  # Just first 6 months for detail

print("DETAILED STATE-BY-STATE DEBUGGING")
print("=" * 80)

states = {
    "Virginia": {"start_month": 1, "initial_patients": 100, "active": True},
    "Florida": {"start_month": 1, "initial_patients": 100, "active": True}
}

df = model.run_projection(
    states,
    {"Virginia": 1.00, "Florida": 1.05},
    {"Virginia": 100, "Florida": 60},
    model.default_rates(),
    model.default_util(),
    settings
)

print("\nRAW DATAFRAME:")
print(df[['Month', 'State', 'New Patients', 'Total Patients', 'Total Revenue']].to_string())

print("\n" + "=" * 80)
print("AGGREGATION CHECK:")
for month in range(1, 7):
    month_data = df[df['Month'] == month]
    print(f"\nMonth {month}:")
    for _, row in month_data.iterrows():
        print(f"  {row['State']}: {row['Total Patients']:.0f} patients")
    total = month_data['Total Patients'].sum()
    print(f"  TOTAL: {total:.0f} patients")