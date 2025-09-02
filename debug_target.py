market_data = {
    "Virginia": {
        "nursing_homes": 280,
        "assisted_living": 450,
        "hospitals": 89,
        "total_snf_beds": 28500,
        "total_alf_beds": 31500,
        "hospital_readmissions": 12000,
        "target_partnerships": {"snf": 100, "alf": 150, "hospitals": 20},
        "notes": "Hill Valley: 10,000 current patients"
    }
}

# Test with Moderate (default)
multiplier = 1.0  # Moderate
state = "Virginia"
data = market_data[state]

snf_partnerships = int(data["target_partnerships"]["snf"] * multiplier)
alf_partnerships = int(data["target_partnerships"]["alf"] * multiplier)
hospital_partnerships = int(data["target_partnerships"]["hospitals"] * multiplier)

avg_snf_beds_per_facility = data["total_snf_beds"] / data["nursing_homes"]
avg_alf_beds_per_facility = data["total_alf_beds"] / data["assisted_living"]

snf_patients = snf_partnerships * (avg_snf_beds_per_facility * 0.85 * 0.75)  # 85% occupancy, 75% RPM eligible
alf_patients = alf_partnerships * (avg_alf_beds_per_facility * 0.88 * 0.70)  # 88% occupancy, 70% RPM eligible
hospital_patients = hospital_partnerships * (data["hospital_readmissions"] * 0.35 / 12)  # 35% of readmissions monthly

state_total = int(snf_patients + alf_patients + hospital_patients)

print(f"Partnership Strategy: Moderate (multiplier={multiplier})")
print(f"SNF Partnerships: {snf_partnerships} x {avg_snf_beds_per_facility:.1f} beds x 0.85 x 0.75 = {snf_patients:.0f} patients")
print(f"ALF Partnerships: {alf_partnerships} x {avg_alf_beds_per_facility:.1f} beds x 0.88 x 0.70 = {alf_patients:.0f} patients")
print(f"Hospital Partnerships: {hospital_partnerships} x {data['hospital_readmissions']*0.35/12:.0f} monthly = {hospital_patients:.0f} patients")
print(f"Total Virginia Target: {state_total:,} patients")
print(f"We want it to be: 19,965 patients")