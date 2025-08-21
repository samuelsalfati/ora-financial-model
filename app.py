import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from model import default_rates, default_util, default_settings, run_model, summarize

st.set_page_config(page_title="Ora Living – WOW Model (Step 1: Virginia)", layout="wide")

st.title("Ora Living – WOW Model (Step 1: Virginia)")
st.caption("Investor-grade, Excel-like editor. Virginia-only baseline with RPM/CCM/TCM; editable rates, utilization, growth & overhead.")

# Session state
if "scenario" not in st.session_state:
    st.session_state.scenario = {
        "rates": default_rates(),
        "util": default_util(),
        "settings": default_settings()
    }

sc = st.session_state.scenario

tabs = st.tabs(["Assumptions","Results","Unit Economics","Export"])

with tabs[0]:
    st.subheader("Billing Code Rates (editable)")
    rates_df = pd.DataFrame(sc["rates"]).T.reset_index().rename(columns={"index":"Code"})
    rates_df = st.data_editor(rates_df, use_container_width=True, num_rows="dynamic")
    sc["rates"] = {r["Code"]: {k: r[k] for k in rates_df.columns if k!="Code"} for _, r in rates_df.iterrows()}

    st.subheader("Utilization / Eligibility (0–1)")
    util_df = pd.DataFrame(sc["util"], index=[0])
    util_df = st.data_editor(util_df, use_container_width=True)
    sc["util"] = util_df.iloc[0].to_dict()

    st.subheader("Global Settings")
    cols = st.columns(3)
    with cols[0]:
        sc["settings"]["months"] = st.number_input("Months", 12, 120, sc["settings"]["months"], 12)
        sc["settings"]["initial_patients"] = st.number_input("Initial patients (Month 1)", 0, 10000, sc["settings"]["initial_patients"], 10)
        sc["settings"]["monthly_growth"] = st.slider("Monthly growth (existing)", 0.0, 0.40, sc["settings"]["monthly_growth"], 0.01)
    with cols[1]:
        sc["settings"]["initial_homes"] = st.number_input("Initial nursing homes", 0, 500, sc["settings"]["initial_homes"], 1)
        sc["settings"]["home_growth_per_year"] = st.number_input("New homes per year", 0, 50, sc["settings"]["home_growth_per_year"])
        sc["settings"]["patients_per_home_growth"] = st.slider("Annual patients/home growth", 0.0, 0.40, sc["settings"]["patients_per_home_growth"], 0.01)
    with cols[2]:
        sc["settings"]["overhead_base"] = st.number_input("Overhead base (monthly)", 0.0, 500000.0, sc["settings"]["overhead_base"], 1000.0)
        sc["settings"]["overhead_cap"] = st.number_input("Overhead cap", 0.0, 500000.0, sc["settings"]["overhead_cap"], 1000.0)
        sc["settings"]["initial_cash"] = st.number_input("Initial cash", -10000000.0, 50000000.0, sc["settings"]["initial_cash"], 10000.0)

df = run_model(sc["rates"], sc["util"], sc["settings"])
sums = summarize(df)

with tabs[1]:
    st.subheader("KPI Summary")
    st.dataframe(sums["kpi"], use_container_width=True)

    st.subheader("Revenue vs Costs vs EBITDA (Monthly)")
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df["Month"], df["Total Revenue"]/1_000_000, label="Revenue (M)")
    ax.plot(df["Month"], df["Total Costs"]/1_000_000, label="Costs (M)")
    ax.plot(df["Month"], df["EBITDA"]/1_000_000, label="EBITDA (M)")
    ax2 = ax.twinx()
    ax2.plot(df["Month"], df["Cash Balance"]/1_000_000, linestyle="--", label="Cash (M)")
    ax.set_xlabel("Month"); ax.set_ylabel("P&L (Millions)"); ax2.set_ylabel("Cash (M)")
    ax.grid(True); ax.legend(loc="upper left")
    st.pyplot(fig)

    st.subheader("Patients & Capacity")
    fig2, ax = plt.subplots(figsize=(10,4))
    ax.plot(df["Month"], df["Total Patients"], label="Total Patients")
    ax2 = ax.twinx()
    ax2.plot(df["Month"], df["RPM_Minutes_Demand"], linestyle="--", label="RPM Minutes Demand")
    ax2.plot(df["Month"], df["Staff_Minutes_Capacity"], linestyle=":", label="Staff Minutes Capacity")
    ax.set_xlabel("Month"); ax.set_ylabel("Patients"); ax2.set_ylabel("Minutes")
    ax.grid(True); ax.legend(loc="upper left")
    st.pyplot(fig2)

with tabs[2]:
    st.subheader("Per-Patient Waterfall (Latest Month)")
    last_m = df["Month"].max()
    row = df[df["Month"]==last_m].iloc[-1]
    revenue_pp = row["Per-Patient Revenue"]
    cost_pp = row["Per-Patient Cost"]
    margin_pp = row["Per-Patient Margin"]

    wf = pd.DataFrame({"Label":["Revenue","Costs","Margin"], "Value":[revenue_pp, -cost_pp, margin_pp]})
    fig3, ax = plt.subplots(figsize=(6,4))
    running = 0
    for i, r in wf.iterrows():
        ax.bar(i, r["Value"], bottom=running if r["Value"]<0 else 0)
        running += r["Value"]
    ax.set_xticks(range(len(wf))); ax.set_xticklabels(wf["Label"])
    ax.set_ylabel("USD per Patient"); ax.grid(True, axis="y")
    st.pyplot(fig3)

    st.subheader("Assumptions Snapshot")
    st.write("Rates")
    st.dataframe(pd.DataFrame(sc["rates"]).T)
    st.write("Utilization")
    st.dataframe(pd.DataFrame([sc["util"]]))

with tabs[3]:
    st.subheader("Export to Excel")
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as xls:
        df.to_excel(xls, index=False, sheet_name="Monthly")
        sums["kpi"].to_excel(xls, index=False, sheet_name="KPI")
        pd.DataFrame(sc["rates"]).T.to_excel(xls, sheet_name="Rates")
        pd.DataFrame([sc["util"]]).to_excel(xls, index=False, sheet_name="Utilization")
        pd.DataFrame([sc["settings"]]).to_excel(xls, index=False, sheet_name="Settings")
    st.download_button("Download Excel", data=out.getvalue(), file_name="ora_va_step1.xlsx")