import model

print("=== FULL MODEL AUDIT ===")
print()

# Check 1: Default settings
settings = model.default_settings()
print("DEFAULT SETTINGS:")
print(f"Initial patients: {settings['initial_patients']:,}")
print(f"Monthly growth: {settings['monthly_growth']*100:.1f}%")  
print(f"Monthly attrition: {settings['monthly_attrition']*100:.1f}%")
print(f"Net growth: {(settings['monthly_growth'] - settings['monthly_attrition'])*100:.1f}%")
print()

# Check 2: What does this mean over 48 months?
initial = 10000  # Hill Valley starting point
net_rate = settings['monthly_growth'] - settings['monthly_attrition']
final_calc = initial * (1 + net_rate) ** 48
print(f"MATH CHECK - Starting with {initial:,} patients:")
print(f"Net growth: {net_rate*100:.1f}% per month")
print(f"After 48 months: {final_calc:,.0f} patients")
print()

# Check 3: Run the actual model
states = {"Virginia": {"start_month": 1, "initial_patients": 10000, "active": True}}
gpci = {"Virginia": 1.0}
homes = {"Virginia": 40}

rates = model.default_rates()
util = model.default_util()

df = model.run_projection(states, gpci, homes, rates, util, settings)

print("ACTUAL MODEL RESULTS:")
month_48 = df[df['Month'] == 48].iloc[0]
print(f"Month 48 patients: {month_48['Total Patients']:,.0f}")
print(f"Month 48 revenue: ${month_48['Total Revenue']:,.0f}")
print(f"Month 48 cash: ${month_48['Cash Balance']:,.0f}")
print()

# Check 4: Max patients cap issue
print("MAX PATIENTS CAP CHECK:")
for month in [1, 12, 24, 36, 48]:
    homes_now = homes["Virginia"] + settings["home_growth_per_year"] * ((month-1)//12)
    pph = 20 * (1+settings["patients_per_home_growth"])**((month-1)//12)
    theoretical_capacity = int(homes_now * pph)
    max_patients = max(theoretical_capacity, 100000)
    
    actual_patients = df[df['Month'] == month].iloc[0]['Total Patients']
    print(f"Month {month}: Capacity={theoretical_capacity:,}, Max={max_patients:,}, Actual={actual_patients:,.0f}")
print()

print("PROBLEMS IDENTIFIED:")
if final_calc > 100000:
    print("❌ Growth rate too high - leads to unrealistic patient counts")
if month_48['Cash Balance'] > 100000000:
    print("❌ Cash balance exploding - working capital or revenue issue") 
if theoretical_capacity < 20000:
    print("❌ Capacity constraint too low - artificially limiting growth")

print()
print("RECOMMENDATION:")
print("Choose ONE approach:")
print("1. Target-based: Set target (80K patients) and calculate required growth rate")
print("2. Growth-based: Set realistic growth rate (0.5% net) and see where it leads")