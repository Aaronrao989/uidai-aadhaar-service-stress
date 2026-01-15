import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- SAFE OPTIONAL IMPORTS ----------------
try:
    import folium
    from streamlit_folium import st_folium
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Aadhaar Service Stress Model",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background */
    .main {
        background-color: #1e293b;
    }
    
    .block-container {
        background-color: #1e293b;
    }
    
    /* Main title styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #f1f5f9;
        text-align: center;
        margin-bottom: 0.3rem;
        padding: 1.5rem 0;
        letter-spacing: -0.02em;
    }
    
    /* Subtitle styling */
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }
    
    /* Section headers */
    h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Metric container styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Metric container background */
    [data-testid="metric-container"] {
        background: #334155;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #475569;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar selectbox */
    [data-testid="stSidebar"] .stSelectbox label {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
    }
    
    /* Button styling */
    .stDownloadButton button {
        background: #475569;
        color: #f1f5f9;
        border: 1px solid #64748b;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .stDownloadButton button:hover {
        background: #64748b;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    }
    
    /* Divider styling */
    hr {
        margin: 2.5rem 0;
        border: none;
        border-top: 1px solid #475569;
    }
    
    /* Info box styling */
    .stAlert {
        background: #334155;
        border-radius: 10px;
        border-left: 4px solid #64748b;
        padding: 1rem;
        color: #e2e8f0;
    }
    
    /* Caption styling */
    .caption-text {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 2rem;
        padding: 1.5rem;
        background: #334155;
        border-radius: 10px;
        border: 1px solid #475569;
        line-height: 1.6;
    }
    
    /* Stress category badge */
    .stress-badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        letter-spacing: 0.02em;
    }
    
    .stress-high {
        background: #dc2626;
        color: #ffffff;
    }
    
    .stress-medium {
        background: #f59e0b;
        color: #ffffff;
    }
    
    .stress-low {
        background: #10b981;
        color: #ffffff;
    }
    
    /* Main container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* All text color override */
    p, span, div {
        color: #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<h1 class="main-title">🏛️ Aadhaar Service Stress Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">UIDAI Data Hackathon 2026 | Real-time Service Analytics</p>', unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("outputs/tables/aadhaar_service_stress_model_output.csv")
    df = df[df["state"].str.contains(r"[A-Za-z]", regex=True)]
    return df

model_df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("### 📍 Select Region")
st.sidebar.markdown("---")

state = st.sidebar.selectbox(
    "🗺️ State",
    sorted(model_df["state"].unique()),
    help="Select a state to view district-level data"
)

district = st.sidebar.selectbox(
    "📌 District",
    sorted(model_df[model_df["state"] == state]["district"].unique()),
    help="Select a district for detailed analysis"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Info")
st.sidebar.info("This dashboard provides real-time insights into Aadhaar service stress across regions.")

row = model_df[
    (model_df["state"] == state) &
    (model_df["district"] == district)
].iloc[0]

# ---------------- METRICS ----------------
st.markdown("### 📈 Key Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Enrolments",
        f"{int(row['total_enrolments']):,}",
        delta=None,
        help="Total number of Aadhaar enrolments"
    )

with col2:
    st.metric(
        "Biometric Updates",
        f"{int(row['total_biometric_updates']):,}",
        delta=None,
        help="Number of biometric update requests"
    )

with col3:
    st.metric(
        "Demographic Updates",
        f"{int(row['total_demographic_updates']):,}",
        delta=None,
        help="Number of demographic update requests"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- SERVICE STRESS ----------------
st.markdown("### 🎯 Service Stress Assessment")

col_a, col_b = st.columns([2, 1])

with col_a:
    st.metric(
        "Service Stress Score",
        f"{row['service_stress_score']:.2f}",
        help="Composite score indicating service load pressure"
    )

with col_b:
    # Determine stress category color
    category = row['stress_category'].lower()
    if 'high' in category:
        badge_class = 'stress-high'
    elif 'medium' in category or 'moderate' in category:
        badge_class = 'stress-medium'
    else:
        badge_class = 'stress-low'
    
    st.markdown(f'<div class="stress-badge {badge_class}">{row["stress_category"]}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Chart with improved styling
fig, ax = plt.subplots(figsize=(10, 2.2))
fig.patch.set_facecolor('#1e293b')
ax.set_facecolor('#334155')

# Color based on stress level
stress_score = row["service_stress_score"]
max_score = model_df["service_stress_score"].max()

if stress_score / max_score > 0.7:
    bar_color = '#dc2626'  # Red for high stress
elif stress_score / max_score > 0.4:
    bar_color = '#f59e0b'  # Orange for moderate stress
else:
    bar_color = '#10b981'  # Green for low stress

ax.barh([""], [stress_score], color=bar_color, height=0.4, alpha=1.0)
ax.set_xlim(0, max_score * 1.05)
ax.set_xlabel("Stress Score", fontsize=11, fontweight='600', color='#cbd5e1')
ax.set_title("Service Stress Indicator", fontsize=14, fontweight='700', color='#f1f5f9', pad=20)
ax.grid(axis='x', alpha=0.15, linestyle='-', linewidth=0.5, color='#64748b')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#64748b')
ax.tick_params(colors='#cbd5e1', labelsize=10)

plt.tight_layout()

img_buffer = BytesIO()
fig.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight", facecolor='#1e293b')
img_buffer.seek(0)

st.pyplot(fig)

col_download1, col_download2, col_download3 = st.columns([1, 1, 1])
with col_download2:
    st.download_button(
        "🖼️ Download Chart (PNG)",
        data=img_buffer,
        file_name=f"service_stress_{state}_{district}.png",
        mime="image/png",
        use_container_width=True
    )

st.divider()

# ---------------- PDF REPORT (DISTRICT) ----------------
def generate_pdf(row):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Aadhaar Service Stress Report")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Generated on: {timestamp}")

    y = height - 120
    c.setFont("Helvetica", 12)

    fields = [
        ("State", row["state"]),
        ("District", row["district"]),
        ("Total Enrolments", f"{int(row['total_enrolments']):,}"),
        ("Biometric Updates", f"{int(row['total_biometric_updates']):,}"),
        ("Demographic Updates", f"{int(row['total_demographic_updates']):,}"),
        ("Service Stress Score", f"{row['service_stress_score']:.2f}"),
        ("Priority Category", row["stress_category"]),
    ]

    for label, value in fields:
        c.drawString(50, y, f"{label}: {value}")
        y -= 22

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

st.markdown("### 📄 Download District Report")

pdf_file = generate_pdf(row)

col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
with col_pdf2:
    st.download_button(
        "📄 Download District Report (PDF)",
        data=pdf_file,
        file_name=f"aadhaar_service_stress_{state}_{district}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.divider()

# ---------------- STATE MAP VIEW ----------------
st.markdown("### 🗺️ State-wise Service Stress Overview")

state_summary = model_df.groupby("state", as_index=False)["service_stress_score"].mean()

if MAP_AVAILABLE:
    india_map = folium.Map(location=[22.5, 78.9], zoom_start=5)

    for _, r in state_summary.iterrows():
        folium.Marker(
            location=[22.5, 78.9],  # conceptual overview
            tooltip=r["state"],
            popup=f"{r['state']}<br>Avg Stress: {r['service_stress_score']:.2f}"
        ).add_to(india_map)

    st_folium(india_map, width=700, height=450)
else:
    st.info("🗺️ Map view unavailable (folium not available in this environment).")

st.divider()

# ---------------- BULK PDF (STATE SUMMARY) ----------------
def generate_state_summary_pdf(df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "State-wise Aadhaar Service Stress Summary")

    y = height - 90
    c.setFont("Helvetica", 10)

    for _, r in df.iterrows():
        c.drawString(
            50, y,
            f"{r['state']}: Avg Stress Score = {r['service_stress_score']:.2f}"
        )
        y -= 18
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

state_pdf = generate_state_summary_pdf(state_summary)

st.markdown("### 📦 Bulk Reports")

col_bulk1, col_bulk2, col_bulk3 = st.columns([1, 2, 1])
with col_bulk2:
    st.download_button(
        "📦 Download State-wise Summary (PDF)",
        data=state_pdf,
        file_name=f"aadhaar_state_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.divider()

st.markdown(
    '<p class="caption-text">✨ This is an explainable decision-support system built using '
    'anonymised Aadhaar enrolment and update data. | UIDAI Data Hackathon 2026</p>',
    unsafe_allow_html=True
)