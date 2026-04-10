import streamlit as st
import requests
import urllib.parse

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Smart Traffic", layout="wide")
st.title("🚦 AI Smart Traffic Navigation")

API_KEY = "AIzaSyAXdNSVduvRGIaBpP8ZvgCNrr8qbz9g67k"

# ---------------- INPUT ---------------- #
col1, col2 = st.columns(2)

with col1:
    source = st.text_input("📍 Start Location", "Gulistan, Dhaka")

with col2:
    destination = st.text_input("🏁 Destination", "Mirpur, Dhaka")

# ---------------- BUTTON ---------------- #
if st.button("Find Best Route"):

    # Encode locations
    encoded_source = urllib.parse.quote(source)
    encoded_destination = urllib.parse.quote(destination)

    # ---------------- AI TRAFFIC API ---------------- #
    try:
        traffic_data = requests.get("http://127.0.0.1:5000/traffic").json()
    except:
        st.error("❌ Backend API not running")
        st.stop()

    pcu = traffic_data.get("pcu", 0)
    signals = traffic_data.get("signals", {})

    # ---------------- GOOGLE DIRECTIONS ---------------- #
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={encoded_source}&destination={encoded_destination}&mode=driving&alternatives=true&key={API_KEY}"

    directions = requests.get(directions_url).json()

    # ---------------- ERROR HANDLING ---------------- #
    if directions.get("status") != "OK":
        st.error(f"❌ Google Directions Error: {directions.get('status')}")
        st.stop()

    if not directions.get("routes"):
        st.error("❌ No route found (Try different location)")
        st.stop()

    # ---------------- EXTRACT ROUTE ---------------- #
    route = directions["routes"][0]["legs"][0]

    distance_text = route["distance"]["text"]
    duration_value = route["duration"]["value"]

    # ---------------- AI TRAFFIC ADJUSTMENT ---------------- #
    if pcu > 10:
        factor = 1.5
    elif pcu > 5:
        factor = 1.2
    else:
        factor = 1.0

    final_time = int((duration_value * factor) / 60)

    # ---------------- LAYOUT ---------------- #
    left, right = st.columns([2, 1])

    # ===== LEFT (MAP) ===== #
    with left:
        st.subheader("🗺️ Current Traffic Overview")

        map_url = f"https://www.google.com/maps/embed/v1/directions?key={API_KEY}&origin={encoded_source}&destination={encoded_destination}"

        st.components.v1.iframe(map_url, height=450)

        st.markdown(f"### 📏 Distance: **{distance_text}**")
        st.markdown(f"### ⏱️ Base Time: **{int(duration_value/60)} min**")
        st.markdown(f"### 🚀 AI Optimized Time: **{final_time} min**")

        st.link_button(
            "📍 Open in Google Maps",
            f"https://www.google.com/maps/dir/{encoded_source}/{encoded_destination}"
        )

    # ===== RIGHT (ANALYSIS) ===== #
    with right:
        st.subheader("📊 Traffic Analysis")

        st.markdown(f"### 🚦 Total PCU: {pcu}")

        if pcu > 10:
            st.error("🔴 Heavy Traffic")
        elif pcu > 5:
            st.warning("🟡 Moderate Traffic")
        else:
            st.success("🟢 Low Traffic")

        st.markdown("### 🚦 Signal Timing")

        for road, time in signals.items():
            st.write(f"Road {road} → {time} sec")

    # ---------------- AI DECISION ---------------- #
    st.subheader("🧠 AI Route Decision")

    if factor > 1.3:
        st.error("⚠️ Heavy congestion detected → Consider alternative route")
    elif factor > 1.1:
        st.warning("⚠️ Moderate traffic → Slight delay expected")
    else:
        st.success("✅ Fastest route selected")

    # ---------------- SIGNAL DETAILS ---------------- #
    st.subheader("🚦 Signal Timing Adjustment")

    for road, time in signals.items():
        red = 120 - time
        st.success(f"Road {road}: 🟢 {time}s | 🔴 {red}s")

    # ---------------- LIVE STATUS ---------------- #
    st.subheader("🚦 Current Signal Status")

    for road, time in signals.items():
        st.progress(time / 120)
        st.write(f"{road}: {time} sec")