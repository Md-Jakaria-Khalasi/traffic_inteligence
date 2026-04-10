from flask import Flask, jsonify
from main import detect_vehicles, calculate_pcu, calculate_signal
from ultralytics import YOLO
import os

app = Flask(__name__)

model = YOLO("yolov8n.pt")
image_path = os.path.join("images", "traffic.jpg")

@app.route("/traffic")
def get_traffic_data():
    try:
        vehicle_count = detect_vehicles(model, image_path)
        total_pcu = calculate_pcu(vehicle_count)
        green_time = calculate_signal(total_pcu)

        return jsonify({
            "vehicle_count": vehicle_count,
            "pcu": total_pcu,
            "signals": green_time
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)