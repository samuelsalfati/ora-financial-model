import model

settings = model.default_settings()

# Calculate staffing costs per patient
clinical = settings['clinical_staff_pmpm']
liaisons = settings['family_care_liaisons_pmpm'] 
admin = settings['admin_staff_pmpm']
ai_factor = settings['ai_efficiency_factor']

total_before_ai = clinical + liaisons + admin
total_after_ai = total_before_ai * ai_factor

print('STAFFING COST BREAKDOWN (per patient per month):')
print(f'Clinical (RNs at 1:350):     ${clinical:.2f}')
print(f'Family Liaisons:             ${liaisons:.2f}')
print(f'Admin/Support (1:150):       ${admin:.2f}')
print(f'Subtotal:                    ${total_before_ai:.2f}')
print(f'After AI efficiency (×{ai_factor}): ${total_after_ai:.2f}')
print()
print('NURSE RATIO CALCULATION:')
print(f'RN monthly cost: $7,500 (at $90k/year)')
print(f'Clinical PMPM: ${clinical:.2f}')
print(f'Patients per RN: {7500/clinical:.0f}')
print()
print('SUPPORT STAFF RATIO:')
print(f'Support monthly cost: $5,000 (at $60k/year)')
print(f'Admin PMPM: ${admin:.2f}')
print(f'Patients per support: {5000/admin:.0f}')