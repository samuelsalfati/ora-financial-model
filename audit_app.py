"""
Audit app_simple.py for VC presentation readiness
"""

print("APP_SIMPLE.PY AUDIT CHECKLIST")
print("=" * 60)

checklist = {
    "✅ Single State Focus": [
        "Remove multi-state complexity",
        "Focus on Virginia/Hill Valley only",
        "Hide confusing options"
    ],
    
    "✅ Key Metrics Clear": [
        "Revenue per patient: $241",
        "Cost per patient: $74",
        "Gross margin: 69%",
        "Target patients: 19,965"
    ],
    
    "✅ Growth Scenarios Work": [
        "Conservative: 5 years to target",
        "On Timeline: 4 years to target",  
        "Aggressive: 3 years to target",
        "Cash balance improves with aggressive"
    ],
    
    "⚠️ Things to Remove/Hide": [
        "Complex multi-state logic",
        "Confusing partnership strategy options",
        "Too many sliders",
        "Technical debugging info"
    ],
    
    "⚠️ Things to Emphasize": [
        "Unit economics",
        "Hill Valley partnership (100 homes)",
        "TCM offset for devices",
        "Path to profitability",
        "Conservative assumptions"
    ],
    
    "🔍 Code Quality": [
        "Remove debug prints",
        "Clean up comments", 
        "Simplify complex sections",
        "Remove test code"
    ]
}

for category, items in checklist.items():
    print(f"\n{category}")
    for item in items:
        print(f"  • {item}")

print("\n" + "=" * 60)
print("\nRECOMMENDED CHANGES:")
print("1. Remove partnership strategy dropdown (just use Moderate)")
print("2. Reduce sliders to only essential ones")
print("3. Clean up Model Overview tab")
print("4. Ensure all numbers are consistent")
print("5. Add clear VC-focused messaging")