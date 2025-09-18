import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="☢️ Radioactive Water Detector", layout="wide")

st.title("☢️ Radioactive Water Contamination Detector")
st.markdown("Developed by **Team AquaGuard**")

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs([
    "🏠 Input Parameters",
    "📊 Safe vs Unsafe Levels",
    "📂 Dataset Viewer",
    "🔥 Heatmap Visualization",
    "🔬 Methodology & Accuracy",
    "💧 Water Treatment Suggestions"
])

# -----------------------------
# Helper Functions
# -----------------------------
def detect_elements(ph, tds, hardness, nitrate):
    elements = []
    if ph < 6.5 or tds > 550 or hardness > 200:
        elements.append("Uranium")
    if nitrate > 40 or tds > 600:
        elements.append("Cesium")
    if ph > 7.5 and hardness < 150:
        elements.append("Radium")
    if not elements:
        elements.append("None Detected")
    return elements

def calculate_risk_score(ph, tds, hardness, nitrate):
    ph_dev = abs(ph - 7)
    tds_dev = max(0, tds - 500)
    hardness_dev = max(0, hardness - 200)
    nitrate_dev = max(0, nitrate - 45)

    score = (0.3 * ph_dev) + (0.25 * tds_dev/10) + (0.2 * hardness_dev/10) + (0.25 * nitrate_dev)
    return min(score, 100)

# -----------------------------
# TAB 1 – User Input
# -----------------------------
with tabs[0]:
    st.subheader("🏠 Enter Water Parameters")

    ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
    tds = st.number_input("TDS (mg/L)", min_value=0, max_value=2000, value=300, step=10)
    hardness = st.number_input("Hardness (mg/L)", min_value=0, max_value=1000, value=150, step=10)
    nitrate = st.number_input("Nitrate (mg/L)", min_value=0, max_value=200, value=20, step=1)

    if st.button("🔍 Analyze Water"):
        elements = detect_elements(ph, tds, hardness, nitrate)
        score = calculate_risk_score(ph, tds, hardness, nitrate)

        risk_label = "✅ Safe" if score < 30 else "⚠️ Moderate Risk" if score < 60 else "☢️ High Risk"

        st.metric("Contamination Risk Score", f"{score:.2f}", delta=risk_label)
        st.markdown(f"**Detected Elements:** {', '.join(elements)}")

# -----------------------------
# TAB 2 – Safe vs Unsafe
# -----------------------------
with tabs[1]:
    st.subheader("📊 Safe vs Unsafe Water Levels")

    safe_ranges = {
        "pH": (6.5, 8.5, ph),
        "TDS (mg/L)": (0, 500, tds),
        "Hardness (mg/L)": (0, 200, hardness),
        "Nitrate (mg/L)": (0, 45, nitrate)
    }

    for param, (low, high, value) in safe_ranges.items():
        col1, col2 = st.columns([1.1, 1.0])  # small graph + value side by side

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[param],
                y=[value],
                name=f"{param} Value",
                marker_color="red" if value < low or value > high else "green"
            ))
            fig.add_shape(
                type="rect",
                x0=-0.5, x1=0.5,
                y0=low, y1=high,
                fillcolor="lightgreen",
                opacity=0.3,
                line_width=0
            )
            fig.update_layout(
                title=f"{param} Level",
                barmode="overlay",
                height=220, width=220,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=False)

        with col2:
            status = "✅ Safe" if low <= value <= high else "☢️ Unsafe"
            st.markdown(
                f"""
                <div style="font-size:18px; color:#FFD300;">
                <b>{param}</b><br>
                ✅ Safe Range: {low} – {high}<br>
                💧 Your Value: <span style="color:{'red' if value < low or value > high else 'lightgreen'};">{value}</span><br>
                ⚖️ Status: {status}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.info("ℹ️ Compare your water parameters above with the WHO safe ranges.")

# -----------------------------
# TAB 3 – Dataset
# -----------------------------
with tabs[2]:
    st.subheader("📂 Dataset Viewer")
    uploaded_file = st.file_uploader("Upload Water Dataset (CSV)", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Add element detection column
        df["Elements Found"] = df.apply(
            lambda row: ", ".join(detect_elements(
                row.get("ph", 7),
                row.get("Solids", 500),
                row.get("Hardness", 150),
                row.get("Nitrate", 20)
            )),
            axis=1
        )

        # Column selector
        selected_cols = st.multiselect("Select Parameters to Display", df.columns.tolist(), default=df.columns.tolist())
        df_filtered = df[selected_cols]

        st.dataframe(df_filtered)

        # Option to download updated CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Updated Dataset", data=csv, file_name="updated_water_data.csv", mime="text/csv")

# -----------------------------
# TAB 4 – Heatmap
# -----------------------------
with tabs[3]:
    st.subheader("🔥 Heatmap Visualization")

    if uploaded_file:
        numeric_df = df.select_dtypes(include=[np.number])

        fig, ax = plt.subplots(figsize=(6, 6))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="RdYlGn", square=True, cbar=True, linewidths=0.5)
        st.pyplot(fig)
    else:
        st.info("Upload a dataset in Tab 3 to view heatmap.")

# -----------------------------
# TAB 5 – Methodology
# -----------------------------
with tabs[4]:
    st.subheader("🔬 How We Detect Elements & Methodology Origin")
    st.write("""
    Our system estimates possible radioactive contamination using **water quality parameters** such as pH, TDS, Hardness, and Nitrate.

    **Methodology:**
    - Based on **correlation studies** of heavy elements in water, from research in **radioactive water monitoring**.
    - Original work: **UNSCEAR** (United Nations Scientific Committee on the Effects of Atomic Radiation) + **WHO Guidelines**.
    - Elevated TDS, unusual pH, hardness, and nitrate often correlate with radioactive elements like Uranium, Cesium, and Radium.

    **Risk Score Formula:**
    ```
    Risk Score = 0.3*(pH deviation) + 0.25*(TDS deviation/10) + 0.2*(Hardness deviation/10) + 0.25*(Nitrate deviation)
    ```

    **Detection Rules:**
    - Uranium → pH < 6.5 OR TDS > 550 OR Hardness > 200
    - Cesium → Nitrate > 40 OR TDS > 600
    - Radium → pH > 7.5 AND Hardness < 150
    - None → If none of the above

    **Risk Levels:**
    - 0–30 → ✅ Safe
    - 31–60 → ⚠️ Moderate Risk
    - 61–100 → ☢️ High Risk

    **Accuracy & Limitations:**
    - Deterministic estimation, not lab-certified.
    - Useful for **preliminary monitoring** & awareness.
    """)

    st.markdown("📌 **Disclaimer:** Confirm with certified laboratory testing for official safety checks.")

# -----------------------------
# TAB 6 – Water Treatment
# -----------------------------
with tabs[5]:
    st.subheader("💧 Water Treatment Suggestions")

    st.write("Treatment methods are suggested based on detected radioactive elements:")

    if uploaded_file:
        for idx, row in df.iterrows():
            elements = row["Elements Found"].split(", ")
            st.markdown(f"### Sample {idx+1} - Elements: {', '.join(elements)}")

            for element in elements:
                if element == "Uranium":
                    st.markdown("""
                    **Treatment for Uranium-contaminated water:**
                    - Reverse Osmosis (RO)
                    - Ion Exchange Resins
                    - Lime Softening
                    - Activated Alumina
                    """)

                elif element == "Cesium":
                    st.markdown("""
                    **Treatment for Cesium-contaminated water:**
                    - Prussian Blue Filters
                    - Zeolite Filtration
                    - Reverse Osmosis
                    """)

                elif element == "Radium":
                    st.markdown("""
                    **Treatment for Radium-contaminated water:**
                    - Ion Exchange (Water Softeners)
                    - Lime Softening
                    - Reverse Osmosis
                    """)

                elif element == "None Detected":
                    st.markdown("✅ No treatment needed. Water is safe.")
    else:
        st.info("⚠️ Upload dataset in Tab 3 or enter water values in Tab 1.")

