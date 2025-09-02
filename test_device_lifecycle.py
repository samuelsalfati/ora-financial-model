print("SMART DEVICE LIFECYCLE MANAGEMENT")
print("="*60)

# Example month with patient flow
new_patients = 400  # New from Hill Valley
leaving_patients = 150  # 3% attrition on 5000 patients

# Device costs
device_cost = 300  # Kit-300
refurb_cost = 50
logistics_cost = 25
recovery_rate = 0.85

print("MONTHLY DEVICE FLOW:")
print(f"New patients needing devices: {new_patients}")
print(f"Patients leaving (attrition): {leaving_patients}")
print(f"Devices recovered (85% rate): {int(leaving_patients * recovery_rate)}")
print()

# Calculate costs OLD WAY (no recovery)
old_way_cost = device_cost * new_patients
print("OLD WAY (No Recovery):")
print(f"Buy {new_patients} new devices × ${device_cost} = ${old_way_cost:,}")
print()

# Calculate costs NEW WAY (with recovery)
recovered = int(leaving_patients * recovery_rate)
net_new_needed = max(0, new_patients - recovered)
reused_devices = min(recovered, new_patients)

new_device_costs = net_new_needed * device_cost
refurb_costs = reused_devices * refurb_cost
logistics_costs = (new_patients + leaving_patients) * logistics_cost

print("SMART WAY (With Recovery):")
print(f"Recovered devices available: {recovered}")
print(f"Devices reused after refurb: {reused_devices}")
print(f"New devices needed: {net_new_needed}")
print()
print("Cost Breakdown:")
print(f"  New devices: {net_new_needed} × ${device_cost} = ${new_device_costs:,}")
print(f"  Refurbishment: {reused_devices} × ${refurb_cost} = ${refurb_costs:,}")
print(f"  Logistics: {new_patients + leaving_patients} × ${logistics_cost} = ${logistics_costs:,}")
print(f"  TOTAL: ${new_device_costs + refurb_costs + logistics_costs:,}")
print()

savings = old_way_cost - (new_device_costs + refurb_costs + logistics_costs)
print(f"MONTHLY SAVINGS: ${savings:,}")
print(f"ANNUAL SAVINGS: ${savings * 12:,}")
print()

# Per-patient economics
old_per_patient = old_way_cost / new_patients
new_per_patient = (new_device_costs + refurb_costs + logistics_costs) / new_patients
print("PER NEW PATIENT:")
print(f"Old way: ${old_per_patient:.2f}/patient")
print(f"Smart way: ${new_per_patient:.2f}/patient")
print(f"Savings: ${old_per_patient - new_per_patient:.2f}/patient ({((old_per_patient - new_per_patient)/old_per_patient)*100:.0f}%)")