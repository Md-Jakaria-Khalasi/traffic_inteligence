# 🚦 AI Smart Traffic Navigation System

> 🚀 AI-powered system for real-time traffic optimization and fastest route recommendation

---

## 📌 Problem

Traffic congestion is one of the biggest challenges in urban cities like Dhaka.  
Most traffic signals are manually controlled or use fixed timing, which does not reflect real-time traffic conditions.

As a result:
- Roads with high traffic remain congested  
- Roads with low traffic waste signal time  
- People lose valuable time every day  

Additionally, traditional navigation systems focus on the **shortest route**, not the **fastest route based on real-time traffic**.

---

## 💡 Solution

We developed an **AI-based Smart Traffic System** that:

- Detects vehicles using computer vision (YOLOv8)  
- Calculates traffic density using PCU (Passenger Car Unit)  
- Dynamically adjusts traffic signal timing  
- Provides users with the **fastest route based on live traffic data**  

---

## ⚙️ Features

- 🚗 AI Vehicle Detection (YOLOv8)  
- 📊 PCU-based Traffic Analysis  
- 🚦 Adaptive Traffic Signal System  
- 🗺️ Google Maps Integration  
- ⏱️ Fastest Route Recommendation (Not Shortest)  
- 📡 Flask API for real-time data  
- 📊 Interactive Dashboard (Streamlit)

---

## 🏗️ System Architecture

Camera Input → YOLO Detection → PCU Calculation → Signal Optimization ↓ Flask API ↓ User Dashboard ↓ Google Maps Integration

---

## 🧠 How It Works

1. Detect vehicles using AI  
2. Calculate traffic density (PCU)  
3. Adjust traffic signal timing dynamically  
4. Fetch route data from Google Maps  
5. Combine traffic data with route data  
6. Recommend the fastest route  

---

## 🎥 Demo

👉 Watch the full project demo here:  
https://youtu.be/FMDIzixul5E  

---

## 🖥️ Tech Stack

- Python  
- YOLOv8 (Ultralytics)  
- Flask (Backend API)  
- Streamlit (Frontend UI)  
- Google Maps API  

---

## 🔑 Setup

1. Get a Google Maps API Key  
2. Enable:
   - Directions API  
   - Maps Embed API  

3. Add your API key in `user_app.py`:
 
 API_KEY = "YOUR_API_KEY"


📦 Requirements
Install dependencies:
Bash
pip install -r requirements.txt

🚀 How to Run
1. Clone the repository
Bash
git clone https://github.com/Md-Jakaria-Khalasi/traffic_inteligence.git
cd traffic_inteligence

2. Run backend API
Bash
python api.py

3. Run user dashboard
Bash
streamlit run user_app.py

📊 Example Output
Total PCU: 8
Signal Timing:
Road A → 60 sec
Road B → 36 sec
Road C → 18 sec
Road D → 10 sec


📁 Project Structure

├── main.py              # AI logic (detection + PCU + signal)
├── api.py               # Flask API
├── user_app.py          # Streamlit UI
├── images/              # Sample input images
├── yolov8n.pt           # Model


🏆 Achievement
🏅 4Th  – Impact Dhaka 2026 Hackathon


👨‍💻 Team
Team Name: Mind Stack
Team Lead: Md. Jakaria Khalasi
Members: Nazmul Hasan,  Md Hasan Mahmud


📜 License
This project is for educational and research purposes.


