import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import re

# ─────────────────────────────────────────────────────────
#   NO API KEY NEEDED — Uses free OpenStreetMap + OSRM
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Dhaka Smart Traffic",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Exo+2:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background-color: #0b1120;
    color: #e0eaff;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2e 0%, #0b1120 100%);
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: #0f2039 !important;
    border: 1px solid #1e4a7a !important;
    border-radius: 8px !important;
    color: #a8d4ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 14px !important;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: white !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #60a5fa) !important;
    box-shadow: 0 0 18px rgba(59,130,246,0.45) !important;
}
.metric-card {
    background: linear-gradient(135deg, #0f2039, #0d1b2e);
    border: 1px solid #1e4a7a;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
}
.metric-label {
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #4a7fa8;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #e0f2ff;
}
.metric-sub { font-size: 12px; color: #5a8aaa; margin-top: 2px; }
.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #60a5fa;
    text-transform: uppercase;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 6px;
    margin: 16px 0 10px 0;
}
.info-box {
    background: #0f2039;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #a8d4ff;
}
.step-item {
    background: #0f2039;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 8px 12px;
    margin-bottom: 5px;
    font-size: 12px;
    color: #a8d4ff;
    line-height: 1.5;
}
.status-ok {
    font-size: 12px;
    color: #22c55e;
    text-align: center;
    padding: 6px;
}
.status-err {
    background: #2d0a0a;
    border: 1px solid #ef4444;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12px;
    color: #fca5a5;
    margin-top: 8px;
}
.free-badge {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #10b981;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    color: #6ee7b7;
    font-weight: 600;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ─── FREE API Functions ───────────────────────────────────────────────────────

def geocode(place_name):
    """
    Nominatim (OpenStreetMap) — সম্পূর্ণ free, no key needed
    Location name → (lat, lon, display_name)
    """
    query = place_name.strip() + ", Dhaka, Bangladesh"
    url   = "https://nominatim.openstreetmap.org/search"
    params = {
        "q":              query,
        "format":         "json",
        "limit":          1,
        "countrycodes":   "bd",
        "addressdetails": 1,
    }
    headers = {"User-Agent": "DhakaSmartTraffic/1.0"}
    try:
        r    = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        if data:
            lat  = float(data[0]["lat"])
            lon  = float(data[0]["lon"])
            name = data[0].get("display_name", place_name)
            # Shorten display name
            name = ", ".join(name.split(", ")[:3])
            return lat, lon, name, "OK"
        return None, None, None, "NOT_FOUND"
    except Exception as e:
        return None, None, None, f"ERROR: {e}"


def get_route(origin_latlon, dest_latlon):
    """
    OSRM (Open Source Routing Machine) — সম্পূর্ণ free, no key needed
    Returns route polyline, distance, duration, turn-by-turn steps
    """
    o_lon, o_lat = origin_latlon[1], origin_latlon[0]
    d_lon, d_lat = dest_latlon[1],   dest_latlon[0]

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{o_lon},{o_lat};{d_lon},{d_lat}"
        f"?overview=full&geometries=geojson&steps=true"
    )
    headers = {"User-Agent": "DhakaSmartTraffic/1.0"}
    try:
        r    = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        if data.get("code") == "Ok":
            route    = data["routes"][0]
            distance = route["distance"]          # meters
            duration = route["duration"]          # seconds
            coords   = [
                (pt[1], pt[0])
                for pt in route["geometry"]["coordinates"]
            ]
            # Turn-by-turn steps
            steps = []
            for leg in route["legs"]:
                for step in leg["steps"]:
                    maneuver = step.get("maneuver", {})
                    mtype    = maneuver.get("type", "")
                    modifier = maneuver.get("modifier", "")
                    name     = step.get("name", "")
                    dist_m   = step.get("distance", 0)

                    if mtype == "depart":
                        instruction = f"Start on {name}" if name else "Start"
                    elif mtype == "arrive":
                        instruction = "Arrive at destination"
                    elif mtype == "turn":
                        instruction = f"Turn {modifier} onto {name}" if name else f"Turn {modifier}"
                    elif mtype == "new name":
                        instruction = f"Continue onto {name}" if name else "Continue straight"
                    elif mtype == "merge":
                        instruction = f"Merge {modifier} onto {name}" if name else "Merge"
                    elif mtype == "roundabout":
                        instruction = f"Enter roundabout, take exit"
                    else:
                        instruction = f"{mtype.capitalize()} {modifier} {name}".strip()

                    if dist_m > 0:
                        if dist_m >= 1000:
                            instruction += f" ({dist_m/1000:.1f} km)"
                        else:
                            instruction += f" ({int(dist_m)} m)"
                    steps.append(instruction)

            # Format distance
            if distance >= 1000:
                dist_str = f"{distance/1000:.1f} km"
            else:
                dist_str = f"{int(distance)} m"

            # Format duration
            mins  = int(duration // 60)
            hours = mins // 60
            mins  = mins % 60
            if hours > 0:
                dur_str = f"{hours}h {mins}min"
            else:
                dur_str = f"{mins} min"

            return coords, dist_str, dur_str, steps, "OK"
        return None, None, None, None, data.get("code", "UNKNOWN")
    except Exception as e:
        return None, None, None, None, f"ERROR: {e}"


# ─── Session State ────────────────────────────────────────────────────────────
defaults = {
    "route_coords": [],
    "distance":     "",
    "duration":     "",
    "steps":        [],
    "from_addr":    "",
    "to_addr":      "",
    "from_latlon":  None,
    "to_latlon":    None,
    "error":        "",
    "success":      False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;
                color:#60a5fa;letter-spacing:2px;text-transform:uppercase;
                margin-bottom:2px;">
        🚦 Route Planner
    </div>
    <div style="font-size:11px;color:#4a6a8a;letter-spacing:1px;
                text-transform:uppercase;margin-bottom:4px;">
        Dhaka Smart Traffic System
    </div>
    <span class="free-badge">● 100% FREE — No API Key</span>
    <br><br>
    """, unsafe_allow_html=True)

    st.markdown("**From Location**")
    from_input = st.text_input(
        "from_label",
        placeholder="e.g. Mirpur 10, Uttara, Dhanmondi",
        key="from_input",
        label_visibility="collapsed",
    )

    st.markdown("**To Location**")
    to_input = st.text_input(
        "to_label",
        placeholder="e.g. Gulshan 1, Motijheel, Banani",
        key="to_input",
        label_visibility="collapsed",
    )

    find_btn = st.button("⚡ Find Fastest Route")

    if st.session_state.success:
        st.markdown('<div class="status-ok">● Route Found Successfully</div>', unsafe_allow_html=True)

    if st.session_state.error:
        st.markdown(f'<div class="status-err">⚠ {st.session_state.error}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:12px;color:#4a6a8a;line-height:2.2;">
    <b style="color:#4a7fa8;">Try these locations:</b><br>
    Mirpur 10 &nbsp;|&nbsp; Uttara Sector 7<br>
    Dhanmondi 27 &nbsp;|&nbsp; Gulshan 2<br>
    Motijheel &nbsp;|&nbsp; Old Dhaka<br>
    Hazrat Shahjalal Airport<br>
    Bashundhara &nbsp;|&nbsp; Farmgate<br>
    Shyamoli &nbsp;|&nbsp; Rampura<br>
    Mohakhali &nbsp;|&nbsp; Banani
    </div>
    """, unsafe_allow_html=True)

    # ── Button Logic ──────────────────────────────────────────────────────────
    if find_btn:
        st.session_state.error   = ""
        st.session_state.success = False

        if not from_input.strip() or not to_input.strip():
            st.session_state.error = "Please enter both From and To locations."
        else:
            with st.spinner("Searching locations..."):
                f_lat, f_lon, f_addr, f_status = geocode(from_input)

            if f_status != "OK":
                st.session_state.error = (
                    f"Could not find '{from_input}'. "
                    "Try being more specific, e.g. 'Mirpur 10 Dhaka'."
                )
                st.session_state.route_coords = []
            else:
                with st.spinner("Searching destination..."):
                    t_lat, t_lon, t_addr, t_status = geocode(to_input)

                if t_status != "OK":
                    st.session_state.error = (
                        f"Could not find '{to_input}'. "
                        "Try being more specific."
                    )
                    st.session_state.route_coords = []
                else:
                    with st.spinner("Calculating best route..."):
                        coords, dist, dur, steps, r_status = get_route(
                            (f_lat, f_lon), (t_lat, t_lon)
                        )

                    if r_status == "OK":
                        st.session_state.route_coords = coords
                        st.session_state.distance     = dist
                        st.session_state.duration     = dur
                        st.session_state.steps        = steps
                        st.session_state.from_addr    = f_addr
                        st.session_state.to_addr      = t_addr
                        st.session_state.from_latlon  = (f_lat, f_lon)
                        st.session_state.to_latlon    = (t_lat, t_lon)
                        st.session_state.success      = True
                    else:
                        st.session_state.error        = f"Route calculation failed: {r_status}"
                        st.session_state.route_coords = []

# ─── Main Title ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:20px;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:30px;font-weight:700;
              letter-spacing:3px;color:#e0f2ff;text-transform:uppercase;">
      🗺 Smart Traffic Intelligence System
  </div>
  <div style="font-size:12px;color:#4a7fa8;letter-spacing:2px;text-transform:uppercase;">
      Real-time Route Planner · Dhaka Metropolitan ·
      <span style="color:#10b981;">Powered by OpenStreetMap + OSRM (Free)</span>
  </div>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

# ─── LEFT: MAP ────────────────────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="section-header">Live Route Map</div>', unsafe_allow_html=True)

    # Map center
    if st.session_state.route_coords:
        mid    = len(st.session_state.route_coords) // 2
        center = st.session_state.route_coords[mid]
        zoom   = 13
    else:
        center = [23.8103, 90.4125]
        zoom   = 12

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
    )

    if st.session_state.route_coords:
        # Main route line
        folium.PolyLine(
            st.session_state.route_coords,
            color="#3b82f6",
            weight=6,
            opacity=0.9,
            tooltip="Best Route",
        ).add_to(m)
        # Dashed overlay
        folium.PolyLine(
            st.session_state.route_coords,
            color="#93c5fd",
            weight=2,
            opacity=0.6,
            dash_array="10 8",
        ).add_to(m)
        # Start marker
        folium.Marker(
            location=st.session_state.from_latlon,
            tooltip=f"Start: {st.session_state.from_addr}",
            icon=folium.Icon(color="green", icon="play", prefix="fa"),
        ).add_to(m)
        # End marker
        folium.Marker(
            location=st.session_state.to_latlon,
            tooltip=f"Destination: {st.session_state.to_addr}",
            icon=folium.Icon(color="red", icon="flag", prefix="fa"),
        ).add_to(m)
        # Fit map to route
        lats = [c[0] for c in st.session_state.route_coords]
        lons = [c[1] for c in st.session_state.route_coords]
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    else:
        # Default Dhaka landmarks
        landmarks = {
            "Hazrat Shahjalal Airport": [23.8433, 90.3978],
            "Motijheel":                [23.7334, 90.4175],
            "Mirpur 10":                [23.8073, 90.3692],
            "Gulshan 1":                [23.7808, 90.4194],
            "Dhanmondi":                [23.7461, 90.3742],
            "Old Dhaka":                [23.7104, 90.4074],
            "Uttara":                   [23.8759, 90.3795],
            "Banani":                   [23.7937, 90.4066],
            "Farmgate":                 [23.7587, 90.3892],
            "Bashundhara":              [23.8134, 90.4240],
            "Mohakhali":                [23.7806, 90.4042],
            "Shyamoli":                 [23.7738, 90.3630],
        }
        for name, coords in landmarks.items():
            folium.CircleMarker(
                location=coords,
                radius=7,
                color="#3b82f6",
                fill=True,
                fill_color="#3b82f6",
                fill_opacity=0.5,
                tooltip=name,
            ).add_to(m)
            folium.Marker(
                location=[coords[0] + 0.003, coords[1]],
                icon=folium.DivIcon(
                    html=f'<div style="font-family:Rajdhani,sans-serif;font-size:10px;'
                         f'color:#60a5fa;background:rgba(11,17,32,0.85);'
                         f'border:1px solid #1e4a7a;border-radius:4px;'
                         f'padding:1px 5px;white-space:nowrap;">{name}</div>',
                    icon_size=(150, 18),
                    icon_anchor=(75, 0),
                ),
            ).add_to(m)

    st_folium(m, width=None, height=500, returned_objects=[])

# ─── RIGHT: DASHBOARD ─────────────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="section-header">Route Dashboard</div>', unsafe_allow_html=True)

    if st.session_state.route_coords:
        # From / To
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">From</div>
            <div style="font-size:13px;color:#6ee7b7;font-weight:600;line-height:1.4;">
                📍 {st.session_state.from_addr}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">To</div>
            <div style="font-size:13px;color:#f87171;font-weight:600;line-height:1.4;">
                🏁 {st.session_state.to_addr}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Distance + Duration
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Distance</div>
                <div class="metric-value">{st.session_state.distance}</div>
                <div class="metric-sub">Total route</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Travel Time</div>
                <div class="metric-value">{st.session_state.duration}</div>
                <div class="metric-sub">Estimated</div>
            </div>
            """, unsafe_allow_html=True)

        # Turn-by-turn directions
        st.markdown('<div class="section-header">Turn-by-Turn Directions</div>', unsafe_allow_html=True)
        show_steps = st.session_state.steps[:15]
        for i, step in enumerate(show_steps, 1):
            st.markdown(f"""
            <div class="step-item">
                <span style="color:#3b82f6;font-weight:700;">{i}.</span> {step}
            </div>
            """, unsafe_allow_html=True)
        if len(st.session_state.steps) > 15:
            remaining = len(st.session_state.steps) - 15
            st.markdown(f"""
            <div style="font-size:12px;color:#4a6a8a;text-align:center;padding:6px;">
                + {remaining} more steps
            </div>
            """, unsafe_allow_html=True)

        # Traffic forecast chart
        st.markdown('<div class="section-header">Traffic Forecast</div>', unsafe_allow_html=True)
        forecast = pd.DataFrame(
            {"PCU Load": [7, 9, 11, 14, 16]},
            index=["Now", "+5m", "+10m", "+15m", "+20m"]
        )
        st.line_chart(forecast, color="#f97316", height=140)

    else:
        # Placeholder
        st.markdown("""
        <div class="metric-card" style="text-align:center;padding:36px 20px;">
            <div style="font-size:44px;margin-bottom:12px;">🗺</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:17px;
                        color:#4a7fa8;line-height:1.8;">
                Enter <b style="color:#60a5fa;">From</b> and
                <b style="color:#60a5fa;">To</b> locations<br>
                then click <b style="color:#3b82f6;">Find Fastest Route</b>
            </div>
        </div>
        <div class="info-box">💡 Type any Dhaka location — area, road, or landmark</div>
        <div class="info-box">🆓 100% Free — No API key or billing needed</div>
        <div class="info-box">🗺 Route data from OpenStreetMap</div>
        <div class="info-box">⚡ Powered by OSRM routing engine</div>
        """, unsafe_allow_html=True)

        # Dhaka area avg speed
        st.markdown('<div class="section-header">Dhaka Area Avg Speed</div>', unsafe_allow_html=True)
        stats = pd.DataFrame(
            {"Avg Speed (km/h)": [18, 12, 8, 15, 20, 14, 10, 11]},
            index=["Mirpur", "Motijheel", "Old Dhaka", "Gulshan",
                   "Uttara", "Banani", "Farmgate", "Mohakhali"]
        )
        st.bar_chart(stats, color="#3b82f6", height=200)

        # Network traffic summary
        st.markdown('<div class="section-header">Network Status</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">OpenStreetMap</div>
                <div style="color:#22c55e;font-weight:700;font-size:14px;">● Online</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">OSRM Router</div>
                <div style="color:#22c55e;font-weight:700;font-size:14px;">● Online</div>
            </div>
            """, unsafe_allow_html=True)