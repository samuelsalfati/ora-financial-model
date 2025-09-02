import model

# Test what happens with multi-state selection
rates = model.default_rates()
util = model.default_util()
settings = model.default_settings()
settings['months'] = 60

print("TESTING MULTI-STATE EBITDA MARGINS")
print("=" * 70)

configs = [
    ("Virginia Only", {
        "Virginia": {"start_month": 1, "initial_patients": 100, "active": True}
    }),
    ("Virginia + Florida (both start Month 1)", {
        "Virginia": {"start_month": 1, "initial_patients": 100, "active": True},
        "Florida": {"start_month": 1, "initial_patients": 100, "active": True}
    }),
    ("All 5 States (all start Month 1)", {
        "Virginia": {"start_month": 1, "initial_patients": 100, "active": True},
        "Florida": {"start_month": 1, "initial_patients": 100, "active": True},
        "Texas": {"start_month": 1, "initial_patients": 100, "active": True},
        "New York": {"start_month": 1, "initial_patients": 100, "active": True},
        "California": {"start_month": 1, "initial_patients": 100, "active": True}
    })
]

for name, states in configs:
    gpci = {
        "Virginia": 1.00,
        "Florida": 1.05,
        "Texas": 1.03,
        "New York": 1.08,
        "California": 1.10
    }
    homes = {
        "Virginia": 100,
        "Florida": 60,
        "Texas": 80,
        "New York": 50,
        "California": 70
    }
    
    # Filter gpci and homes for active states only
    active_gpci = {k: gpci[k] for k in states.keys()}
    active_homes = {k: homes[k] for k in states.keys()}
    
    df = model.run_projection(states, active_gpci, active_homes, rates, util, settings)
    
    # Check month 48 results
    month_48 = df[df['Month'] == 48].iloc[0]
    revenue = month_48['Total Revenue']
    costs = month_48['Total Costs']
    ebitda = month_48['EBITDA']
    patients = month_48['Total Patients']
    margin = (ebitda / revenue * 100) if revenue > 0 else 0
    
    print(f"\n{name}:")
    print(f"  Month 48 Patients: {patients:,.0f}")
    print(f"  Month 48 Revenue: ${revenue:,.0f}")
    print(f"  Month 48 Costs: ${costs:,.0f}")
    print(f"  Month 48 EBITDA: ${ebitda:,.0f}")
    print(f"  EBITDA Margin: {margin:.1f}%")
    print(f"  Revenue/Patient: ${revenue/patients:.0f}")
    print(f"  Cost/Patient: ${costs/patients:.0f}")

print("\n" + "=" * 70)
print("EXPECTED BEHAVIOR:")
print("- More states = more patients = better margins (economies of scale)")
print("- Cost per patient should DECREASE with more states")
print("- EBITDA margin should INCREASE with more states")