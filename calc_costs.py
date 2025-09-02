# Quick calculation of actual cost per patient
staffing = 41.79  # After AI efficiency
platform = 15  # Average platform cost

# Device economics with TCM offset
device_gross = 300  # New device cost
tcm_offset = 193.50  # Average TCM billing (60% × $192.50 + 30% × $260)
device_net = device_gross - tcm_offset  # $106.50 net cost
device_recovery_value = device_gross * 0.85  # 85% recovery rate
device_monthly = device_net / 12  # Amortized over 12 months

overhead = 8  # Per patient overhead from model

total_cost = staffing + platform + device_monthly + overhead
print(f'Cost breakdown per patient:')
print(f'  Staffing: ${staffing:.2f}')
print(f'  Platform: ${platform:.2f}')
print(f'  Device (net after TCM): ${device_monthly:.2f}')
print(f'  Overhead: ${overhead:.2f}')
print(f'  TOTAL: ${total_cost:.2f}/month')
print(f'\nDevice Economics Detail:')
print(f'  Gross device cost: ${device_gross:.2f}')
print(f'  TCM offset: -${tcm_offset:.2f}')
print(f'  Net device cost: ${device_net:.2f}')
print(f'  Monthly amortized: ${device_monthly:.2f}')