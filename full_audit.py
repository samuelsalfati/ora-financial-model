import model
import pandas as pd

print("="*80)
print("COMPREHENSIVE ORA LIVING FINANCIAL MODEL AUDIT")
print("="*80)

# Load all default settings
rates = model.default_rates()
util = model.default_util()  
settings = model.default_settings()
multi_state = model.default_multi_state_config()

print("\n1. GROWTH MODEL ASSUMPTIONS")
print("-"*50)
print(f"Starting patients: {settings['initial_patients']:,}")
print(f"Monthly growth rate: {settings['monthly_growth']*100:.1f}%")
print(f"Monthly attrition rate: {settings['monthly_attrition']*100:.1f}%")
print(f"Net monthly growth: {(settings['monthly_growth'] - settings['monthly_attrition'])*100:.2f}%")
print(f"Equivalent annual growth: {((1 + settings['monthly_growth'] - settings['monthly_attrition'])**12 - 1)*100:.1f}%")

# Calculate 5-year projection
final_patients = settings['initial_patients'] * (1 + settings['monthly_growth'] - settings['monthly_attrition'])**60
print(f"Projected patients at Month 60: {final_patients:,.0f}")

print("\n2. REVENUE MODEL - BILLING CODES")
print("-"*50)
print("RPM (Remote Patient Monitoring) Codes:")
for code in ['99453', '99454', '99457', '99458', '99091']:
    rate = rates[code]['rate']
    multiplier = rates[code]['multiplier']
    utilization = {
        '99453': util['rpm_setup'],
        '99454': util['rpm_16day'], 
        '99457': util['rpm_20min'],
        '99458': util['rpm_40min'],
        '99091': util['md_99091']
    }[code]
    monthly_rev = rate * multiplier * utilization
    print(f"  {code}: ${rate:.2f} × {multiplier:.2f}x × {utilization*100:.0f}% = ${monthly_rev:.2f}/patient/month")

print("\nCCM (Chronic Care Management) Codes:")
for code in ['99490', '99439', '99487', '99489']:
    if code in rates:
        rate = rates[code]['rate']
        multiplier = rates[code]['multiplier']
        utilization = {
            '99490': util['ccm_99490'],
            '99439': util['ccm_99439'],
            '99487': util.get('ccm_99487', 0),
            '99489': util.get('ccm_99489', 0)
        }[code]
        monthly_rev = rate * multiplier * utilization
        print(f"  {code}: ${rate:.2f} × {multiplier:.2f}x × {utilization*100:.0f}% = ${monthly_rev:.2f}/patient/month")

# Calculate total revenue per patient
total_rpm_rev = (rates['99454']['rate'] * util['rpm_16day'] +
                rates['99457']['rate'] * util['rpm_20min'] +
                rates['99458']['rate'] * rates['99458']['multiplier'] * util['rpm_40min'] +
                rates['99091']['rate'] * util['md_99091'])

total_ccm_rev = (rates['99490']['rate'] * util['ccm_99490'] +
                rates['99439']['rate'] * rates['99439']['multiplier'] * util['ccm_99439'] +
                rates['99487']['rate'] * util.get('ccm_99487', 0) +
                rates['99489']['rate'] * util.get('ccm_99489', 0))

total_monthly_rev = (total_rpm_rev + total_ccm_rev) * util['collection_rate']
print(f"\nTOTAL REVENUE PER PATIENT: ${total_monthly_rev:.0f}/month")
print(f"Collection rate applied: {util['collection_rate']*100:.0f}%")

print("\n3. COST STRUCTURE BREAKDOWN")
print("-"*50)

# Staffing costs per patient
clinical_pmpm = settings.get('clinical_staff_pmpm', 18.0)
family_pmpm = settings.get('family_care_liaisons_pmpm', 3.0)
admin_pmpm = settings.get('admin_staff_pmpm', 4.0)
total_staff_pmpm = clinical_pmpm + family_pmpm + admin_pmpm

print("Staffing Costs (Per Patient Per Month):")
print(f"  Clinical Staff: ${clinical_pmpm:.2f}")
print(f"  Family Liaisons: ${family_pmpm:.2f}")
print(f"  Admin Staff: ${admin_pmpm:.2f}")
print(f"  Total Staffing: ${total_staff_pmpm:.2f}/patient/month")

# AI efficiency
ai_efficiency = settings.get('ai_efficiency_factor', 0.85)
print(f"  AI Efficiency Factor: {ai_efficiency*100:.0f}% (saves {(1-ai_efficiency)*100:.0f}%)")
print(f"  Actual Staffing Cost: ${total_staff_pmpm * ai_efficiency:.2f}/patient/month")

print(f"\nMedical Directors:")
print(f"  Base salary: ${settings.get('medical_directors_base', 70000):,}/year")
print(f"  Additional per state: ${settings.get('medical_directors_per_state', 15000):,}/year")

print(f"\nState Management Hierarchy:")
print(f"  Head of State: ${settings.get('head_of_state_salary', 12000):,}/month per state")
print(f"  Managers: ${settings.get('manager_salary', 7500):,}/month each")
print(f"  Patients per manager: {settings.get('patients_per_manager', 2500):,}")

print("\n4. OVERHEAD & OPERATIONAL COSTS")
print("-"*50)
print(f"Base overhead: ${settings.get('overhead_base', 25000):,}/month")
print(f"Per-patient overhead: ${settings.get('overhead_per_patient', 2.0):.2f}/patient/month")
print(f"Overhead cap: ${settings.get('overhead_cap', 150000):,}/month (economies of scale)")
print(f"Marketing budget: {settings.get('marketing_budget_percent', 0.08)*100:.0f}% of revenue")

print("\nExecutive Team Hiring Timeline:")
print("  Month 24+: CMO hired ($20K/month) when >3,000 patients")
print("  Month 30+: CTO hired ($22K/month) when >5,000 patients") 
print("  Month 36+: CFO hired ($18K/month) when >8,000 patients")

print("\n5. MULTI-STATE EXPANSION")
print("-"*50)
for state, config in multi_state.items():
    print(f"{state}:")
    print(f"  Launch month: {config['start_month']}")
    print(f"  Initial patients: {config['initial_patients']:,}")
    print(f"  GPCI multiplier: {config['gpci']:.2f}")
    print(f"  Active by default: {config.get('active', False)}")

print(f"\nState Expansion Costs:")
print(f"  One-time setup: ${settings.get('state_setup_cost', 50000):,} per new state")
print(f"  Annual licensing: ${settings.get('state_licensing_annual', 25000):,} per state")

print("\n6. VENDOR & TECHNOLOGY COSTS")
print("-"*50)
vendor_presets = model.default_vendor_presets()
for vendor_name, config in vendor_presets.items():
    print(f"{vendor_name}:")
    if config.tiers:
        print(f"  Tiered pricing: {config.tiers}")
    if config.flat_pmpm:
        print(f"  Flat PMPM: ${config.flat_pmpm}/patient/month")
    print(f"  Monthly software fee: ${config.monthly_software_fee:,}")
    if config.hardware_kits:
        print(f"  Hardware kits: {config.hardware_kits}")
    if config.dev_capex > 0:
        print(f"  Dev capex: ${config.dev_capex:,}")

print(f"\nActive vendor: {settings.get('initial_vendor', 'Impilo')}")
migration = settings.get('migration_month', None)
if migration:
    print(f"Migration to Ora at month: {migration}")

print("\n7. WORKING CAPITAL ASSUMPTIONS")
print("-"*50)
print(f"Medicare collection days: {settings.get('dso_medicare', 45)} days")
print(f"Commercial collection days: {settings.get('dso_commercial', 75)} days")
print(f"Medicare/Medicaid mix: {settings.get('payer_mix_medicare', 0.65)*100:.0f}%")
print(f"Payment terms to vendors: {settings.get('dpo_vendors', 30)} days")

print("\n8. UNIT ECONOMICS SUMMARY")
print("-"*50)
print(f"Revenue per patient: ~${total_monthly_rev:.0f}/month")
print(f"Staffing cost per patient: ~${total_staff_pmpm * ai_efficiency:.0f}/month")
print(f"Overhead per patient: ~${settings.get('overhead_per_patient', 2.0):.0f}/month")
estimated_cost_pmpm = (total_staff_pmpm * ai_efficiency + 
                      settings.get('overhead_per_patient', 2.0) + 
                      15)  # Estimate for platform/hardware
print(f"Estimated total cost: ~${estimated_cost_pmpm:.0f}/patient/month")
print(f"Estimated margin: ~${total_monthly_rev - estimated_cost_pmpm:.0f}/patient/month")
print(f"Estimated margin %: {((total_monthly_rev - estimated_cost_pmpm)/total_monthly_rev)*100:.0f}%")

print("\n9. KEY MODEL ASSUMPTIONS & RISKS")
print("-"*50)
print("ASSUMPTIONS:")
print("✓ 1 RN can manage 100 patients (industry standard: 2-3 per 100)")
print("✓ AI reduces staffing needs by 15%")  
print("✓ Medicare/Medicaid pays reliably with 95% collection rate")
print("✓ Marketing spend at 8% of revenue (typical for healthcare)")
print("✓ Overhead scales then caps at $150K (economies of scale)")
print("✓ Management hierarchy scales with patient count")

print("\nPOTENTIAL RISKS:")
print("⚠ Medicare reimbursement rate changes")
print("⚠ Clinical staff shortage/wage inflation")
print("⚠ Higher than expected patient attrition")
print("⚠ Technology/platform cost increases")
print("⚠ Regulatory compliance costs")

print("\n" + "="*80)
print("END OF COMPREHENSIVE AUDIT")
print("="*80)