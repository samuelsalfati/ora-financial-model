import model

print("🎯 BILLING UTILIZATION CONTROLS DEMONSTRATION")
print("="*60)
print()

rates = model.default_rates()

print("📊 WHAT EACH SLIDER CONTROLS:")
print("-"*40)
print()

print("🔧 RPM SERVICES:")
print(f"• Device Monitoring (99454): ${rates['99454']['rate']}/month × [slider %] of patients")
print(f"• Base Management (99457): ${rates['99457']['rate']}/month × [slider %] of patients") 
print(f"• Additional Sessions (99458): ${rates['99458']['rate']}/month × 1.35 multiplier × [slider %] of patients")
print(f"• Physician Review (99091): ${rates['99091']['rate']}/month × [slider %] of patients")
print()

print("🔧 CCM/PCM SERVICES:")
print(f"• Base CCM (99490): ${rates['99490']['rate']}/month × [slider %] of patients")
print(f"• Additional CCM (99439): ${rates['99439']['rate']}/month × 1.2 multiplier × [slider %] of patients")
print(f"• Base PCM (99426): ${rates['99426']['rate']}/month × [slider %] of patients")
print()

print("🔧 ENHANCED SERVICES (if enabled):")
print(f"• Complex CCM (99487): ${rates['99487']['rate']}/month × [slider %] of patients")
print(f"• Complex Additional (99489): ${rates['99489']['rate']}/month × [60% of complex CCM %]")
print()

print("💡 EXAMPLE IMPACT:")
print("-"*30)
print("If you change 'Additional Sessions (99458)' from 40% to 60%:")
base_revenue = rates['99458']['rate'] * 1.35 * 0.40
higher_revenue = rates['99458']['rate'] * 1.35 * 0.60
difference = higher_revenue - base_revenue
print(f"Revenue increases by ${difference:.2f}/patient/month")
print(f"On 10,000 patients = ${difference * 10000:,.0f}/month more revenue")
print()

print("🎛️ USE CASES:")
print("-"*20)
print("• Lower rates for conservative billing")
print("• Higher rates for aggressive/optimized billing") 
print("• Adjust based on patient acuity mix")
print("• Model different care management scenarios")
print("• Test impact of improved patient engagement")