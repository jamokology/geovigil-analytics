import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# ── i18n ────────────────────────────────────────────────────────────────────
TEXTS = {
    "es": {
        "page_title":     "Orbit Sentinel — Detección de Pistas Ilegales",
        "title":          "Orbit Sentinel",
        "subtitle":       "Sistema de detección de pistas clandestinas · Perú",
        "caption":        "Resultados del análisis por IA de imágenes satelitales",
        "filter_header":  "Filtros",
        "slider_label":   "Confianza mínima (%)",
        "legend_title":   "Nivel de confianza",
        "legend_high":    "Alta  ≥ 85%",
        "legend_mid":     "Media  70–84%",
        "legend_low":     "Baja  < 70%",
        "metric_label":   "Detecciones visibles",
        "metric_total":   "de un total de",
        "table_expander": "Lista de detecciones",
        "col_lat":        "Latitud",
        "col_lon":        "Longitud",
        "col_conf":       "Confianza",
        "col_date":       "Fecha de detección",
        "popup_conf":     "Confianza",
        "popup_date":     "Detectado",
        "popup_coord":    "Coordenadas",
        "lang_toggle":    "🇬🇧 English",
        "last_update":    "Última actualización del lote",
        "data_status":    "Estado de datos",
        "status_demo":    "Demo — datos simulados",
    },
    "en": {
        "page_title":     "Orbit Sentinel — Illegal Runway Detection",
        "title":          "Orbit Sentinel",
        "subtitle":       "Clandestine airstrip detection system · Peru",
        "caption":        "AI satellite imagery analysis results",
        "filter_header":  "Filters",
        "slider_label":   "Minimum confidence (%)",
        "legend_title":   "Confidence level",
        "legend_high":    "High  ≥ 85%",
        "legend_mid":     "Medium  70–84%",
        "legend_low":     "Low  < 70%",
        "metric_label":   "Visible detections",
        "metric_total":   "out of",
        "table_expander": "Detection list",
        "col_lat":        "Latitude",
        "col_lon":        "Longitude",
        "col_conf":       "Confidence",
        "col_date":       "Detected at",
        "popup_conf":     "Confidence",
        "popup_date":     "Detected",
        "popup_coord":    "Coordinates",
        "lang_toggle":    "🇪🇸 Español",
        "last_update":    "Last batch update",
        "data_status":    "Data status",
        "status_demo":    "Demo — simulated data",
    },
}

# ── ダミーデータ ─────────────────────────────────────────────────────────────
DETECTIONS = pd.DataFrame(
    [
        {"lat": -3.7491,  "lon": -73.2538, "confidence": 0.91, "detected_at": "2025-03-15 08:22"},
        {"lat": -5.1843,  "lon": -75.0152, "confidence": 0.84, "detected_at": "2025-03-15 08:45"},
        {"lat": -4.5621,  "lon": -74.1834, "confidence": 0.72, "detected_at": "2025-03-15 09:10"},
        {"lat": -6.3217,  "lon": -76.5409, "confidence": 0.63, "detected_at": "2025-03-15 09:33"},
        {"lat": -7.1562,  "lon": -75.8823, "confidence": 0.55, "detected_at": "2025-03-15 09:55"},
        {"lat": -3.2984,  "lon": -72.6741, "confidence": 0.88, "detected_at": "2025-03-16 07:18"},
        {"lat": -8.8043,  "lon": -74.9215, "confidence": 0.77, "detected_at": "2025-03-16 08:02"},
        {"lat": -13.5317, "lon": -72.8818, "confidence": 0.69, "detected_at": "2025-03-17 10:05"},
        {"lat": -11.2451, "lon": -75.3394, "confidence": 0.82, "detected_at": "2025-03-17 10:30"},
        {"lat": -14.0672, "lon": -73.4129, "confidence": 0.58, "detected_at": "2025-03-17 11:00"},
        {"lat": -12.5934, "lon": -70.0817, "confidence": 0.95, "detected_at": "2025-03-18 06:45"},
        {"lat": -11.8763, "lon": -71.3452, "confidence": 0.87, "detected_at": "2025-03-18 07:20"},
        {"lat": -13.1289, "lon": -69.6543, "confidence": 0.74, "detected_at": "2025-03-18 07:55"},
        {"lat": -0.1834,  "lon": -75.8712, "confidence": 0.61, "detected_at": "2025-03-19 09:00"},
        {"lat": -1.5423,  "lon": -77.1234, "confidence": 0.79, "detected_at": "2025-03-19 09:40"},
    ]
)

CONFIDENCE_COLORS = {
    "high":   {"hex": "#E53935", "folium": "red"},
    "medium": {"hex": "#FB8C00", "folium": "orange"},
    "low":    {"hex": "#1E88E5", "folium": "blue"},
}


def confidence_tier(conf: float) -> str:
    if conf >= 0.85:
        return "high"
    elif conf >= 0.70:
        return "medium"
    return "low"


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Orbit Sentinel",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* dark header bar */
    [data-testid="stAppViewContainer"] { background: #0f1117; }
    [data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] * { color: #e6edf3 !important; }
    /* metric cards */
    [data-testid="stMetric"] {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #58a6ff !important; }
    /* title area */
    .orbit-title { color: #e6edf3; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0; }
    .orbit-subtitle { color: #8b949e; font-size: 0.95rem; margin-top: 2px; margin-bottom: 0; }
    .orbit-caption { color: #58a6ff; font-size: 0.8rem; margin-top: 6px; }
    /* legend dots */
    .legend-dot { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 7px; vertical-align: middle; }
    /* section divider */
    hr { border-color: #30363d !important; }
    /* expander */
    [data-testid="stExpander"] { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Language state ────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "es"

t = TEXTS[st.session_state.lang]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button(t["lang_toggle"], use_container_width=True):
        st.session_state.lang = "en" if st.session_state.lang == "es" else "es"
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {t['filter_header']}")
    min_conf = st.slider(t["slider_label"], min_value=0, max_value=100, value=50, step=5) / 100.0

    st.markdown("---")
    st.markdown(f"**{t['legend_title']}**")
    for tier, label_key in [("high", "legend_high"), ("medium", "legend_mid"), ("low", "legend_low")]:
        color = CONFIDENCE_COLORS[tier]["hex"]
        st.markdown(
            f'<span class="legend-dot" style="background:{color}"></span>{t[label_key]}',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    total = len(DETECTIONS)
    filtered_count = len(DETECTIONS[DETECTIONS["confidence"] >= min_conf])
    st.metric(t["metric_label"], f"{filtered_count}  /  {total}")

    st.markdown("---")
    st.markdown(f"**{t['data_status']}**")
    st.markdown(
        f'<span style="color:#3fb950;font-size:0.85rem">● {t["status_demo"]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span style="color:#8b949e;font-size:0.8rem">{t["last_update"]}: 2025-03-19</span>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f'<p class="orbit-title">🛰️ {t["title"]}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="orbit-subtitle">{t["subtitle"]}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="orbit-caption">{t["caption"]}</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Map ───────────────────────────────────────────────────────────────────────
df_filtered = DETECTIONS[DETECTIONS["confidence"] >= min_conf].reset_index(drop=True)

m = folium.Map(
    location=[-9.19, -75.0],
    zoom_start=6,
    tiles="CartoDB dark_matter",
)

for _, row in df_filtered.iterrows():
    tier = confidence_tier(row["confidence"])
    color = CONFIDENCE_COLORS[tier]["folium"]
    popup_html = f"""
    <div style="font-family:sans-serif;font-size:13px;min-width:180px">
        <b style="font-size:14px">{t['popup_conf']}: {row['confidence']*100:.1f}%</b><br>
        <hr style="margin:6px 0;border-color:#ddd">
        📅 {t['popup_date']}: {row['detected_at']}<br>
        📍 {t['popup_coord']}: {row['lat']:.4f}, {row['lon']:.4f}
    </div>
    """
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=9,
        color=color,
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=folium.Popup(popup_html, max_width=230),
        tooltip=f"{row['confidence']*100:.1f}%",
    ).add_to(m)

st_folium(m, use_container_width=True, height=620, returned_objects=[])

# ── Detection table ──────────────────────────────────────────────────────────
with st.expander(f"📋  {t['table_expander']}", expanded=False):
    display_df = df_filtered.copy()
    display_df["confidence"] = (display_df["confidence"] * 100).map("{:.1f}%".format)
    display_df.columns = [t["col_lat"], t["col_lon"], t["col_conf"], t["col_date"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
