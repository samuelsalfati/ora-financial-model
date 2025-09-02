import model

rates = model.default_rates()
util = model.default_util()
settings = model.default_settings()

print('COMPREHENSIVE REVENUE AUDIT')
print('='*60)
print()
print('MONTHLY RECURRING REVENUE (per patient):')
print('-'*40)

# RPM Revenue
rpm_99454 = rates['99454']['rate'] * util['rpm_16day']
rpm_99457 = rates['99457']['rate'] * util['rpm_20min']
rpm_99458 = rates['99458']['rate'] * rates['99458']['multiplier'] * util['rpm_40min']
rpm_99091 = rates['99091']['rate'] * util['md_99091']

print(f'99454 (Device): ${rates["99454"]["rate"]} x {util["rpm_16day"]*100:.0f}% = ${rpm_99454:.2f}')
print(f'99457 (20min): ${rates["99457"]["rate"]} x {util["rpm_20min"]*100:.0f}% = ${rpm_99457:.2f}')
print(f'99458 (40min): ${rates["99458"]["rate"]} x {rates["99458"]["multiplier"]} x {util["rpm_40min"]*100:.0f}% = ${rpm_99458:.2f}')
print(f'99091 (MD Review): ${rates["99091"]["rate"]:.2f} x {util["md_99091"]*100:.0f}% = ${rpm_99091:.2f}')
print(f'RPM TOTAL: ${rpm_99454 + rpm_99457 + rpm_99458 + rpm_99091:.2f}')
print()

# CCM Revenue
ccm_99490 = rates['99490']['rate'] * util['ccm_99490']
ccm_99439 = rates['99439']['rate'] * rates['99439']['multiplier'] * util['ccm_99439']

print(f'99490 (CCM Base): ${rates["99490"]["rate"]} x {util["ccm_99490"]*100:.0f}% = ${ccm_99490:.2f}')
print(f'99439 (CCM Add): ${rates["99439"]["rate"]} x {rates["99439"]["multiplier"]} x {util["ccm_99439"]*100:.0f}% = ${ccm_99439:.2f}')
print(f'CCM TOTAL: ${ccm_99490 + ccm_99439:.2f}')
print()

# Enhanced billing
print('ENHANCED BILLING (if enabled):')
print('-'*40)
ccm_99487 = rates['99487']['rate'] * util.get('ccm_99487', 0.25)
ccm_99489 = rates['99489']['rate'] * util.get('ccm_99489', 0.15)
pcm_99426 = rates['99426']['rate'] * util.get('pcm_99426', 0.15)
pcm_99427 = rates['99427']['rate'] * rates['99427']['multiplier'] * util.get('pcm_99427', 0.08)

print(f'99487 (Complex CCM): ${rates["99487"]["rate"]:.2f} x {util.get("ccm_99487", 0.25)*100:.0f}% = ${ccm_99487:.2f}')
print(f'99489 (Complex Add): ${rates["99489"]["rate"]:.2f} x {util.get("ccm_99489", 0.15)*100:.0f}% = ${ccm_99489:.2f}')
print(f'99426 (PCM Base): ${rates["99426"]["rate"]} x {util.get("pcm_99426", 0.15)*100:.0f}% = ${pcm_99426:.2f}')
print(f'99427 (PCM Add): ${rates["99427"]["rate"]} x {rates["99427"]["multiplier"]} x {util.get("pcm_99427", 0.08)*100:.0f}% = ${pcm_99427:.2f}')
print(f'ENHANCED TOTAL: ${ccm_99487 + ccm_99489 + pcm_99426 + pcm_99427:.2f}')
print()

# TCM Revenue
print('ONE-TIME REVENUE (per NEW patient):')
print('-'*40)
tcm_99495 = rates['99495']['rate'] * util['tcm_99495']
tcm_99496 = rates['99496']['rate'] * util['tcm_99496']
rpm_setup = rates['99453']['rate'] * util['rpm_setup']

print(f'99495 (TCM Moderate): ${rates["99495"]["rate"]} x {util["tcm_99495"]*100:.0f}% = ${tcm_99495:.2f}')
print(f'99496 (TCM High): ${rates["99496"]["rate"]} x {util["tcm_99496"]*100:.0f}% = ${tcm_99496:.2f}')
print(f'99453 (RPM Setup): ${rates["99453"]["rate"]} x {util["rpm_setup"]*100:.0f}% = ${rpm_setup:.2f}')
print(f'ONE-TIME TOTAL: ${tcm_99495 + tcm_99496 + rpm_setup:.2f}')
print()

# Summary
basic_monthly = rpm_99454 + rpm_99457 + rpm_99458 + rpm_99091 + ccm_99490 + ccm_99439
enhanced_monthly = basic_monthly + ccm_99487 + ccm_99489 + pcm_99426 + pcm_99427
one_time = tcm_99495 + tcm_99496 + rpm_setup

print('SUMMARY (with 95% collection rate):')
print('-'*40)
print(f'Basic Monthly: ${basic_monthly:.2f} x 95% = ${basic_monthly * 0.95:.2f}')
print(f'Enhanced Monthly: ${enhanced_monthly:.2f} x 95% = ${enhanced_monthly * 0.95:.2f}')
print(f'One-time (new patient): ${one_time:.2f} x 95% = ${one_time * 0.95:.2f}')
print()
print('BLENDED REVENUE (assuming 400 new patients/month on 5000 patient base):')
one_time_portion = (one_time * 400) / 5400  # One-time revenue spread across all patients
print(f'Monthly recurring: ${enhanced_monthly * 0.95:.2f}')
print(f'One-time portion: ${one_time_portion * 0.95:.2f}')
print(f'TOTAL per patient: ${(enhanced_monthly + one_time_portion) * 0.95:.2f}')