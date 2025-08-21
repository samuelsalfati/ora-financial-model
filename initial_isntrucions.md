# Ora Living – Interactive Financial Model (Investor-Ready)

## 🔑 Core Requirements for the “Wow” Model

### 1. Dynamic, Interactive Excel-Feel
- Spreadsheet-style interface where investors can directly adjust:
  - Number of patients
  - Provider staffing (MD, NP, RN ratios)
  - Vendor choice: **Impilo OR CareSimple OR Proprietary**
  - Billing code mix (RPM, CCM, PCM, TCM, AWV)
  - Device cost assumptions
  - Reimbursement rates (state-by-state Medicare differences)
- Instant recalculation of revenue, costs, and EBITDA like Excel.

---

### 2. Billing Code Integration
- Must include:  
  - **RPM:** 99453, 99454, 99457, 99458, 99091  
  - **CCM:** 99490, 99439  
  - **PCM:** 99426 (30 min) + add-ons  
  - **TCM (Transitional Care)** and **AWV (Annual Wellness Visit)** as *theoretical upside*.
- Toggle billing codes ON/OFF dynamically → shows effect on revenue.
- Display “missed revenue opportunities” to highlight upside potential.

---

### 3. Vendor Scenario Toggle
- **Impilo**: no dev cost, standard SaaS fees, standard devices.  
- **CareSimple**: same as above.  
- **Proprietary**: higher upfront dev cost, lower long-term margin.  
- Mutually exclusive (either/or).  
- Visualize the **path** → start with vendor → shift to proprietary after X months.

---

### 4. Scaling Logic
- Scale patients: **500 → 10,000 → 100,000** (as per deck).  
- Phase by **state expansion**:
  - Virginia → Florida → Texas → New York → California.  
- Show **unit economics per patient by state** (align with business deck).

---

### 5. Outputs / Visuals (Wow Factor)
- 📊 **Unit Economics by State** – bar chart (interactive).  
- 📈 **EBITDA & Cash Curve** – line graph with scenario toggles.  
- 🔀 **Vendor Comparison** – side-by-side charts.  
- 🧮 **Billing Code Mix Sensitivity** – stacked bar or waterfall chart.  
- 📑 **Mini-Dashboard Summary** – key takeaways auto-generated from assumptions.

---

### 6. Investor-Friendly Touches
- Clean UI – financial “Excel vibe,” not overly app-like.  
- **Download button** → Export to Excel (so investors can play offline).  
- Highlight **risk/mitigation** tie-ins (e.g., adoption risk → patient ramp slider).

---

## 🚀 Development Steps

1. **Foundation**
   - Skeleton Streamlit app with sidebar assumptions + dynamic outputs.

2. **Billing Codes Engine**
   - Map each CPT code → reimbursement × frequency × eligible patient subset.
   - Toggle ON/OFF for dynamic scenarios.

3. **Vendor Module**
   - Mutually exclusive selection (Impilo / CareSimple / Proprietary).
   - Adjust costs + margins accordingly.

4. **Scaling Logic**
   - Add patient growth by state.
   - Sliders for adoption %, unit economics by state output.

5. **Wow Visuals**
   - Interactive Plotly charts:
     - EBITDA curve
     - State-by-state economics
     - Vendor comparisons

6. **Export / Sharing**
   - Export assumptions + outputs to Excel/PDF for investor follow-up.

---

## 🎯 Why This Wows Investors
When pitching Andersen Horowitz:
- They can **play with the model live**.
- Adjust patient growth, add/remove billing codes, or switch vendors.
- Instantly see the **financial impact**.
- Demonstrates both **technical depth** and **business clarity**.
