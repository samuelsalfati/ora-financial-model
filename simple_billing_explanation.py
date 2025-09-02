import model

print("🎯 SIMPLE BILLING EXPLANATION - ALL ARE PERCENTAGES!")
print("="*60)
print()

rates = model.default_rates()

print("📋 THINK OF IT AS: 'What % of patients get each service?'")
print("-"*55)
print()

print("✅ BASIC ELIGIBILITY (Yes/No services):")
print("• Device Monitoring (99454): 90% of patients get RPM devices")
print("• Management (99457): 85% of patients get 20min management calls") 
print("• MD Review (99091): 50% of patients need doctor review")
print("• CCM (99490): 60% of patients qualify for chronic care management")
print("• PCM (99426): 15% of patients have single chronic condition needing PCM")
print()

print("➕ ADDITIONAL SERVICES (Extra care for some patients):")
print("• Additional Sessions (99458): 40% of patients need EXTRA RPM sessions")
print("• Additional CCM (99439): 20% of patients need EXTRA CCM time")
print()

print("💰 THE MATH IS SIMPLE:")
print("-"*25)
print()
print("Device Monitoring Revenue:")
print(f"${rates['99454']['rate']:.2f} × 90% × 10,000 patients = ${rates['99454']['rate'] * 0.90 * 10000:,.0f}/month")
print()

print("Additional Sessions Revenue:")
print(f"${rates['99458']['rate']:.2f} × 1.35 (built-in multiplier) × 40% × 10,000 = ${rates['99458']['rate'] * 1.35 * 0.40 * 10000:,.0f}/month")
print("📝 Note: 99458 has a built-in 1.35× multiplier because it's more intensive")
print()

print("Additional CCM Revenue:")
print(f"${rates['99439']['rate']:.2f} × 1.20 (built-in multiplier) × 20% × 10,000 = ${rates['99439']['rate'] * 1.20 * 0.20 * 10000:,.0f}/month")
print("📝 Note: 99439 has a built-in 1.20× multiplier because it's extra time")
print()

print("🔄 WHEN YOU CHANGE THE SLIDERS:")
print("-"*35)
print("Change 'Additional Sessions (99458) %' from 40% to 50%:")
old_revenue = rates['99458']['rate'] * 1.35 * 0.40 * 10000
new_revenue = rates['99458']['rate'] * 1.35 * 0.50 * 10000
print(f"Revenue goes from ${old_revenue:,.0f} to ${new_revenue:,.0f}")
print(f"Difference: +${new_revenue - old_revenue:,.0f}/month")
print()

print("Change 'Additional CCM (99439) %' from 20% to 25%:")
old_ccm = rates['99439']['rate'] * 1.20 * 0.20 * 10000
new_ccm = rates['99439']['rate'] * 1.20 * 0.25 * 10000
print(f"Revenue goes from ${old_ccm:,.0f} to ${new_ccm:,.0f}")
print(f"Difference: +${new_ccm - old_ccm:,.0f}/month")
print()

print("🎛️ SUMMARY:")
print("-"*12)
print("ALL sliders are percentages of patients!")
print("• Basic services = % who get the service at all")
print("• Additional services = % who need EXTRA care")
print("• Some codes have built-in multipliers (like 1.35× for 99458)")
print("• The math: Rate × Multiplier × Your% × Total Patients")