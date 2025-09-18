import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
import json
import time
from streamlit_autorefresh import st_autorefresh

# ================= AUTO-REFRESH =================
st_autorefresh(interval=5000, limit=None, key="datarefresh")

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Radioactive Water Contamination Detector", layout="wide")

# ================= CUSTOM CSS =================
css_block = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
* { font-family: 'Bebas Neue', sans-serif !important; }
html, body, [class*="css"] { background-color: #0a0a0a; color: #e8f5e9; min-height: 100vh; }
h1.app-title { text-align: center; color: #FFD300; font-size: 52px; margin-bottom: 4px; text-shadow: 0 0 10px #FFD300, 0 0 28px #FF7518; }
p.app-sub { text-align: center; color: #39FF14; margin-top: 0; font-size: 20px; text-shadow: 0 0 10px #39FF14; }
.stTabs [role="tablist"] button { background: #101010 !important; color: #39FF14 !important; border-radius: 12px !important; border: 1px solid rgba(57,255,20,0.3) !important; margin-right: 6px !important; padding: 8px 14px !important; transition: all .18s ease; font-size: 16px !important; }
.stTabs [role="tablist"] button:hover { background: #39FF14 !important; color: black !important; transform: translateY(-2px) scale(1.03); box-shadow: 0 0 18px rgba(57,255,20,0.15); }
.stTabs [role="tablist"] button[aria-selected="true"] { background: linear-gradient(90deg, #FFD300, #FF7518) !important; color: black !important; border: 1px solid #FFD300 !important; box-shadow: 0 0 26px rgba(255,211,0,0.35); }
</style>
"""
st.markdown(css_block, unsafe_allow_html=True)

# ================= GOOGLE SHEETS CONNECTION USING SECRET =================
json_key = st.secrets["google_service_account"]["json_key"]  # matches your secrets.toml
creds_dict = json.loads(json_key)
creds = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(creds)
sheet = gc.open("Water Data").sheet1  # Replace with your Google Sheet name

# ================= FETCH DATA =================
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    latest = df.iloc[-1]
    ph = float(latest['pH'])
    tds = float(latest['TDS'])
    location = latest.get('Location', "Unknown")
else:
    ph, tds, location = 7.0, 300.0, "Unknown"

# ================= RISK CALCULATION =================
def predict_contamination(ph, tds):
    score = 0
    if ph < 6.5 or ph > 8.5: score += 50
    if tds > 500: score += 50
    return score

score = predict_contamination(ph, tds)
if score < 30:
    result = '✅ Safe: No significant contamination detected.'
elif score < 60:
    result = '⚠️ Moderate Risk: Some traces possible.'
else:
    result = '☢️ High Risk: Potential contamination detected!'

# ================= UI =================
st.markdown("<h1 class='app-title'>💧☢️ Radioactive Water Contamination Detector</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-sub'>AI/ML Powered Water Safety | Live Data from ESP8266</p>", unsafe_allow_html=True)

tabs = st.tabs(["🔬 Latest Reading", "📊 Safe vs Unsafe", "⚠️ Awareness"])

# ---- TAB 1: Latest Reading ----
with tabs[0]:
    st.subheader(f"📍 Location: {location}")
    st.write(f"💧 pH: {ph}")
    st.write(f"🧪 TDS: {tds} mg/L")
    st.markdown(f"<p style='font-size:20px; color:#FFD300;'>{result}</p>", unsafe_allow_html=True)

    # Animated Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=0,
        title={'text': "Risk Score %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "red" if score >= 60 else "orange" if score >= 30 else "#39FF14"},
            'steps': [
                {'range': [0, 30], 'color': "#39FF14"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "red"}
            ],
        }
    ))
    gauge_placeholder = st.empty()
    for i in range(0, int(score)+1, 2):
        fig.update_traces(value=i)
        gauge_placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(0.02)

# ---- TAB 2: Safe vs Unsafe ----
with tabs[1]:
    st.subheader("📊 pH & TDS Status")
    safe_ranges = {
        "pH": (6.5, 8.5, ph),
        "TDS (mg/L)": (0, 500, tds)
    }
    for param, (low, high, value) in safe_ranges.items():
        status = "✅ Safe" if low <= value <= high else "⚠️ Unsafe"
        color = "#39FF14" if low <= value <= high else "red"
        st.markdown(f"**{param}**: {value} → <span style='color:{color};'>{status}</span>", unsafe_allow_html=True)

# ---- TAB 3: Awareness ----
with tabs[2]:
    st.subheader("⚠️ Radioactive Water Risks")
    st.markdown("""
    - Long-term exposure to contaminated water can increase cancer risk.
    - High TDS or abnormal pH may indicate unsafe water.
    - Always check your local water safety guidelines.
    """)

# Footer
st.markdown("---")
st.markdown('<p style="text-align:center; color:#FFD300;">👨‍💻 Developed by Karthikeyan</p>', unsafe_allow_html=True)
st.markdown("---")

# ---- Show Full Data Table ----
st.subheader("📈 All Recorded Data")
st.dataframe(df)
