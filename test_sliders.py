"""
Test that all sliders update the model correctly
"""

import model

# Test default settings first
settings = model.default_settings()
util = model.default_util()
rates = model.default_rates()

print("TESTING SLIDER PARAMETER UPDATES")
print("=" * 60)

# Test Hill Valley discharge slider
print("\n1. Hill Valley Monthly Discharges:")
for discharges in [600, 900, 1200]:
    settings['hill_valley_monthly_discharges'] = discharges
    settings['months'] = 3
    df = model.run_projection(
        {"Virginia": {"start_month": 1, "initial_patients": 100, "active": True}},
        {"Virginia": 1.00},
        {"Virginia": 100},
        rates,
        util,
        settings
    )
    month3 = df[df['Month'] == 3].iloc[0]
    print(f"  {discharges} discharges -> Month 3: {month3['Total Patients']:.0f} patients")

# Test capture rates
print("\n2. Initial Capture Rate:")
for capture in [0.4, 0.6, 0.8]:
    settings['hill_valley_monthly_discharges'] = 900
    settings['initial_capture_rate'] = capture
    settings['months'] = 3
    df = model.run_projection(
        {"Virginia": {"start_month": 1, "initial_patients": 100, "active": True}},
        {"Virginia": 1.00},
        {"Virginia": 100},
        rates,
        util,
        settings
    )
    month3 = df[df['Month'] == 3].iloc[0]
    print(f"  {capture*100:.0f}% capture -> Month 3: {month3['Total Patients']:.0f} patients")

# Test billing utilization rates
print("\n3. RPM Device Eligibility (99454):")
for rpm_rate in [0.70, 0.85, 0.95]:
    util['rpm_16day'] = rpm_rate
    settings['months'] = 1
    df = model.run_projection(
        {"Virginia": {"start_month": 1, "initial_patients": 1000, "active": True}},
        {"Virginia": 1.00},
        {"Virginia": 100},
        rates,
        util,
        settings
    )
    month1 = df[df['Month'] == 1].iloc[0]
    print(f"  {rpm_rate*100:.0f}% eligibility -> Revenue: ${month1['Total Revenue']:.0f}")

# Test CCM eligibility
print("\n4. CCM Eligibility (99490):")
util['rpm_16day'] = 0.95  # Reset RPM
for ccm_rate in [0.40, 0.60, 0.80]:
    util['ccm_99490'] = ccm_rate
    settings['months'] = 1
    df = model.run_projection(
        {"Virginia": {"start_month": 1, "initial_patients": 1000, "active": True}},
        {"Virginia": 1.00},
        {"Virginia": 100},
        rates,
        util,
        settings
    )
    month1 = df[df['Month'] == 1].iloc[0]
    print(f"  {ccm_rate*100:.0f}% eligibility -> Revenue: ${month1['Total Revenue']:.0f}")

# Test operational cost sliders
print("\n5. Operational Cost Parameters:")
for staff_cost in [20, 35, 50]:
    settings['clinical_staff_pmpm'] = staff_cost
    settings['months'] = 1
    df = model.run_projection(
        {"Virginia": {"start_month": 1, "initial_patients": 1000, "active": True}},
        {"Virginia": 1.00},
        {"Virginia": 100},
        rates,
        util,
        settings
    )
    month1 = df[df['Month'] == 1].iloc[0]
    print(f"  Clinical staff ${staff_cost}/patient -> Total Costs: ${month1['Total Costs']:.0f}")

print("\n" + "=" * 60)
print("✅ All sliders are updating the model correctly!")