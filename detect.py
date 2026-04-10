from ultralytics import YOLO

# load model
model = YOLO("yolov8n.pt")

# run detection
results = model("images/traffic.jpg")

# class names
names = model.names

# vehicle count dictionary
vehicle_count = {}

for r in results:
    for cls in r.boxes.cls:
        label = names[int(cls)]

        if label not in vehicle_count:
            vehicle_count[label] = 0

        vehicle_count[label] += 1

# print vehicle count
print("Vehicle Count:", vehicle_count)

# ---------------- PCU PART ---------------- #

# PCU values
pcu_map = {
    "car": 1,
    "bus": 3,
    "truck": 3,
    "motorcycle": 0.3,
    "person": 0
}

# calculate total PCU
total_pcu = 0

for vehicle, count in vehicle_count.items():
    if vehicle in pcu_map:
        total_pcu += pcu_map[vehicle] * count

print("Total PCU:", total_pcu)