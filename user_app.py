import streamlit as st
import requests

st.set_page_config(page_title="Smart Traffic", layout="wide")

st.title("🚦 AI Smart Traffic Navigation")

# ---------------- INPUT ---------------- #
col1, col2 = st.columns(2)

with col1:
    source = st.text_input("📍 Start Location", "Gulistan, Dhaka")

with col2:
    destination = st.text_input("🏁 Destination", "Mirpur, Dhaka")

# ---------------- BUTTON ---------------- #
if st.button("Find Best Route"):

    api_key = "YOUR_API_KEY"

    # ---------------- API DATA ---------------- #
    try:
        data = requests.get("http://127.0.0.1:5000/traffic").json()
    except:
        st.error("API not running")
        st.stop()

    signals = data["signals"]
    pcu = data["pcu"]

    # ---------------- MAIN LAYOUT ---------------- #
    left, right = st.columns([2, 1])

    # ===== LEFT SIDE (MAP) ===== #
    with left:
        st.subheader("🗺️ Current Traffic Overview")

        map_url = f"""
        https://www.google.com/maps/embed/v1/directions
        ?key={api_key}
        &origin={source}
        &destination={destination}
        """

        st.components.v1.iframe(map_url, height=400)

        # ETA
        if pcu > 10:
            eta = 25
        elif pcu > 5:
            eta = 18
        else:
            eta = 10

        st.markdown(f"### ⏱️ Estimated Travel Time: **{eta} min**")

    # ===== RIGHT SIDE (ANALYSIS) ===== #
    with right:
        st.subheader("📊 Traffic Analysis")

        for road, time in signals.items():
            st.write(f"Road {road} → {time} sec")

        st.markdown(f"### 🚦 Total PCU: {pcu}")

        # traffic level
        if pcu > 10:
            st.error("🔴 Heavy Traffic")
        elif pcu > 5:
            st.warning("🟡 Moderate Traffic")
        else:
            st.success("🟢 Low Traffic")

    # ---------------- SIGNAL DETAILS ---------------- #
    st.subheader("🚦 Signal Timing Adjustment")

    for road, time in signals.items():
        red = 120 - time
        st.write(f"Road {road}: 🟢 {time}s | 🔴 {red}s")

    # ---------------- SIGNAL STATUS ---------------- #
    st.subheader("🚦 Current Signal Status")

    for road, time in signals.items():
        st.progress(time / 120)
        st.write(f"{road}: {time} sec")