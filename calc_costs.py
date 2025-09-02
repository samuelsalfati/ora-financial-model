# Quick calculation of actual cost per patient
staffing = 41.79  # After AI efficiency
platform = 15  # Average platform cost
device_amortized = 66 / 12  # Device cost spread over 12 months
overhead = 8  # Per patient overhead from model

total_cost = staffing + platform + device_amortized + overhead
print(f'Cost breakdown per patient:')
print(f'  Staffing: ${staffing:.2f}')
print(f'  Platform: ${platform:.2f}')
print(f'  Device (amortized): ${device_amortized:.2f}')
print(f'  Overhead: ${overhead:.2f}')
print(f'  TOTAL: ${total_cost:.2f}/month')