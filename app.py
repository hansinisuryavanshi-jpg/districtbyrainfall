import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(page_title="District Rainfall", layout="centered")

# ── Rain Theme CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #87CEFA;
    text-shadow: 0px 0px 10px #00BFFF;
    margin-bottom: 4px;
}
.sub-title {
    text-align: center;
    font-size: 16px;
    color: #E0F7FA;
    margin-bottom: 30px;
}
.rain-icon {
    text-align: center;
    font-size: 65px;
    animation: bounce 2s infinite;
}
@keyframes bounce {
    50% { transform: translateY(-10px); }
}
.metric-card {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(135,206,250,0.35);
    border-radius: 14px;
    padding: 16px 10px;
    text-align: center;
}
.metric-label {
    font-size: 12px;
    color: #B0D4EA;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-value {
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
}
.section-header {
    color: #87CEFA;
    font-size: 18px;
    font-weight: bold;
    margin-top: 24px;
    margin-bottom: 4px;
}
div[data-testid="stSelectbox"] label {
    color: white !important;
    font-weight: bold;
}
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Load CSV data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("notebook/district wise rainfall normal(1).csv")
    # Standardize text
    df["STATE_UT_NAME"] = df["STATE_UT_NAME"].str.strip().str.title()
    df["DISTRICT"]      = df["DISTRICT"].str.strip().str.title()
    return df

df_all = load_data()

MONTHS     = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='rain-icon'>🌧️</div>
<div class='main-title'>District-wise Annual Rainfall</div>
<div class='sub-title'>Explore normal rainfall data across 641 districts of India</div>
""", unsafe_allow_html=True)

# ── State selector ────────────────────────────────────────────────────────
states = ["— Select State —"] + sorted(df_all["STATE_UT_NAME"].unique().tolist())
state = st.selectbox("🗺️ Select State", states)

# ── District selector (filtered) ─────────────────────────────────────────
if state != "— Select State —":
    districts_in_state = sorted(df_all[df_all["STATE_UT_NAME"] == state]["DISTRICT"].unique().tolist())
    district = st.selectbox("📍 Select District", ["— Select District —"] + districts_in_state)
else:
    district = "— Select District —"
    st.selectbox("📍 Select District", ["— Select District —"], disabled=True)

# ── Display data ──────────────────────────────────────────────────────────
if state != "— Select State —" and district != "— Select District —":
    row = df_all[(df_all["STATE_UT_NAME"] == state) & (df_all["DISTRICT"] == district)].iloc[0]

    monthly  = [float(row[m]) for m in MONTHS]
    annual   = float(row["ANNUAL"])
    peak_mm  = max(monthly)
    peak_mo  = MONTH_LABELS[monthly.index(peak_mm)]
    dry_mm   = min(monthly)
    dry_mo   = MONTH_LABELS[monthly.index(dry_mm)]
    monsoon  = float(row["Jun-Sep"])
    monsoon_pct = monsoon / annual * 100 if annual > 0 else 0

    # ── Metric cards ──────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("Annual Total",   f"{annual:,.1f} mm"),
        ("Peak Month",     peak_mo),
        ("Peak Rainfall",  f"{peak_mm:.1f} mm"),
        ("Driest Month",   dry_mo),
        ("Monsoon Share",  f"{monsoon_pct:.0f}%"),
    ]
    for col, (label, value) in zip([c1, c2, c3, c4, c5], metrics):
        col.markdown(f"""
        <div class='metric-card'>
          <div class='metric-label'>{label}</div>
          <div class='metric-value'>{value}</div>
        </div>""", unsafe_allow_html=True)

    # ── Seasonal breakdown ────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Monthly Rainfall (mm)</div>", unsafe_allow_html=True)
    chart_df = pd.DataFrame({"Month": MONTH_LABELS, "Rainfall (mm)": monthly}).set_index("Month")
    st.bar_chart(chart_df, color="#00BFFF", height=280)

    # ── Seasonal summary ──────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🌤️ Seasonal Summary</div>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    seasonal = [
        ("Winter\nJan–Feb",   float(row["Jan-Feb"])),
        ("Pre-Monsoon\nMar–May", float(row["Mar-May"])),
        ("Monsoon\nJun–Sep",  float(row["Jun-Sep"])),
        ("Post-Monsoon\nOct–Dec", float(row["Oct-Dec"])),
    ]
    season_colors = ["#5B8DB8", "#F4A460", "#00BFFF", "#66CDAA"]
    for col, (label, val) in zip([s1, s2, s3, s4], seasonal):
        col.markdown(f"""
        <div class='metric-card'>
          <div class='metric-label' style='white-space:pre-line'>{label}</div>
          <div class='metric-value'>{val:.1f} mm</div>
        </div>""", unsafe_allow_html=True)

    # ── Raw data table ────────────────────────────────────────────────────
    with st.expander("📋 View monthly data table"):
        table_df = pd.DataFrame({
            "Month":        MONTH_LABELS,
            "Rainfall (mm)": [round(v, 1) for v in monthly],
            "% of Annual":   [f"{v/annual*100:.1f}%" if annual > 0 else "—" for v in monthly],
        })
        st.dataframe(
            table_df.style.highlight_max("Rainfall (mm)", color="#1E5F8A")
                          .highlight_min("Rainfall (mm)", color="#1a3a2a"),
            use_container_width=True,
            hide_index=True,
        )

    # ── Compare across districts ──────────────────────────────────────────
    st.markdown("<div class='section-header'>📈 All Districts in {}</div>".format(state), unsafe_allow_html=True)
    state_df = df_all[df_all["STATE_UT_NAME"] == state][["DISTRICT","ANNUAL"]].copy()
    state_df = state_df.sort_values("ANNUAL", ascending=False).reset_index(drop=True)
    state_df.columns = ["District", "Annual Rainfall (mm)"]
    state_df["Annual Rainfall (mm)"] = state_df["Annual Rainfall (mm)"].round(1)
    # highlight selected district
    def highlight_selected(row):
        if row["District"].lower() == district.lower():
            return ["background-color: rgba(0,191,255,0.25); font-weight:bold"] * len(row)
        return [""] * len(row)
    st.dataframe(
        state_df.style.apply(highlight_selected, axis=1)
                      .bar(subset=["Annual Rainfall (mm)"], color="#1E5F8A"),
        use_container_width=True,
        hide_index=True,
        height=min(400, (len(state_df) + 1) * 36),
    )

else:
    st.markdown("""
    <div style='text-align:center; padding:40px 0; color:#87CEFA; font-size:16px;'>
        👆 Select a State and District above to explore rainfall data
    </div>
    """, unsafe_allow_html=True)