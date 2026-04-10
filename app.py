import streamlit as st
from main import get_multi_road_pcu, calculate_signal_from_roads
from ultralytics import YOLO
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Traffic AI", layout="wide")

st.title("🚦 AI Smart Traffic Control System")

# ---------------- LOAD MODEL ---------------- #
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# ---------------- LIVE BUTTON ---------------- #
if st.button("▶ Start Live Monitoring"):

    placeholder = st.empty()

    for _ in range(10):  # simulate realtime

        road_pcu = get_multi_road_pcu(model)
        green_time = calculate_signal_from_roads(road_pcu)

        with placeholder.container():

            st.subheader("📹 Live Camera Feeds")

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            with col1:
                st.image("images/roadA.jpg", caption=f"Road A | PCU: {road_pcu['A']}")

            with col2:
                st.image("images/roadB.jpg", caption=f"Road B | PCU: {road_pcu['B']}")

            with col3:
                st.image("images/roadC.jpg", caption=f"Road C | PCU: {road_pcu['C']}")

            with col4:
                st.image("images/roadD.jpg", caption=f"Road D | PCU: {road_pcu['D']}")

            # ---------------- SIGNAL ---------------- #
            st.subheader("🚦 Signal Timing")

            for road, time_sec in green_time.items():
                st.success(f"Road {road} → Green: {time_sec} sec")

            # ---------------- PROGRESS ---------------- #
            st.subheader("🚦 Live Signal View")

            for road, time_sec in green_time.items():
                st.progress(time_sec / 120)
                st.write(f"{road}: {time_sec} sec")

            # ---------------- GRAPH ---------------- #
            st.subheader("📈 Traffic Analysis")

            roads = list(road_pcu.keys())
            pcu_values = list(road_pcu.values())

            fig, ax = plt.subplots()
            ax.bar(roads, pcu_values)
            ax.set_ylabel("PCU")
            ax.set_title("Road-wise Traffic Density")

            st.pyplot(fig)

        time.sleep(2)