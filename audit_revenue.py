import model
import pandas as pd

# Get default settings
rates = model.default_rates()
util = model.default_util()

# Calculate per-patient revenue with default settings
total_revenue_per_patient = 0
print('📊 PER-PATIENT REVENUE BREAKDOWN (Default Settings)')
print('='*60)

# RPM codes - using correct keys from default_util
rpm_codes = {
    '99454': ('Device Supply', util.get('rpm_16day', 0.90)),
    '99457': ('Management', util.get('rpm_20min', 0.85)),
    '99458': ('Additional Sessions', util.get('rpm_40min', 0.40)),
    '99091': ('MD Review', util.get('md_99091', 0.50))
}

print('\nRPM SERVICES:')
rpm_total = 0
for code, (name, pct) in rpm_codes.items():
    rate = rates[code]['rate']
    mult = rates[code]['multiplier']
    revenue = rate * mult * pct
    rpm_total += revenue
    print(f'  {code} {name:20s}: ${rate:.2f} × {mult:.2f} × {pct:.0%} = ${revenue:.2f}')

# CCM codes - using correct keys
ccm_codes = {
    '99490': ('Base CCM', util.get('ccm_99490', 0.60)),
    '99439': ('Additional CCM', util.get('ccm_99439', 0.20))
}

print('\nCCM SERVICES:')
ccm_total = 0
for code, (name, pct) in ccm_codes.items():
    rate = rates[code]['rate']
    mult = rates[code]['multiplier']
    revenue = rate * mult * pct
    ccm_total += revenue
    print(f'  {code} {name:20s}: ${rate:.2f} × {mult:.2f} × {pct:.0%} = ${revenue:.2f}')

# PCM codes - check if they exist in default_util
pcm_codes = {
    '99426': ('Base PCM', 0.15)  # Hardcoding since not in default_util
}

print('\nPCM SERVICES:')
pcm_total = 0
for code, (name, pct) in pcm_codes.items():
    rate = rates[code]['rate']
    mult = rates[code]['multiplier']
    revenue = rate * mult * pct
    pcm_total += revenue
    print(f'  {code} {name:20s}: ${rate:.2f} × {mult:.2f} × {pct:.0%} = ${revenue:.2f}')

total_revenue_per_patient = rpm_total + ccm_total + pcm_total

print('\n' + '-'*60)
print(f'TOTAL RPM:  ${rpm_total:.2f}')
print(f'TOTAL CCM:  ${ccm_total:.2f}')
print(f'TOTAL PCM:  ${pcm_total:.2f}')
print(f'\n🎯 TOTAL PER PATIENT: ${total_revenue_per_patient:.2f}/month')
print(f'\nTarget was ~$245/patient, current is ${total_revenue_per_patient:.2f}')
if abs(total_revenue_per_patient - 245) < 10:
    print('✅ Revenue per patient is on target!')
else:
    diff = total_revenue_per_patient - 245
    print(f'⚠️  Off by ${abs(diff):.2f} {"(too high)" if diff > 0 else "(too low)"}')