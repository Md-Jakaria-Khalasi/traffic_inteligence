from ultralytics import YOLO

# ---------------- PCU MAP ---------------- #
pcu_map = {
    "car": 1,
    "bus": 3,
    "truck": 3,
    "motorcycle": 0.3,
    "person": 0
}

# ---------------- DETECTION ---------------- #
def detect_vehicles(model, image_path):
    results = model(image_path)
    names = model.names

    vehicle_count = {}

    for r in results:
        for cls in r.boxes.cls:
            label = names[int(cls)]

            if label not in vehicle_count:
                vehicle_count[label] = 0

            vehicle_count[label] += 1

    return vehicle_count

# ---------------- PCU ---------------- #
def calculate_pcu(vehicle_count):
    total_pcu = 0

    for vehicle, count in vehicle_count.items():
        if vehicle in pcu_map:
            total_pcu += pcu_map[vehicle] * count

    return total_pcu

# ---------------- MULTI ROAD PCU ---------------- #
def get_multi_road_pcu(model):
    road_images = {
        "A": "images/roadA.jpg",
        "B": "images/roadB.jpg",
        "C": "images/roadC.jpg",
        "D": "images/roadD.jpg"
    }

    road_pcu = {}

    for road, path in road_images.items():
        vehicle_count = detect_vehicles(model, path)
        pcu = calculate_pcu(vehicle_count)
        road_pcu[road] = pcu

    return road_pcu

# ---------------- SIGNAL LOGIC ---------------- #
def calculate_signal_from_roads(road_pcu):
    cycle_time = 120
    MIN_TIME = 10

    total = sum(road_pcu.values())
    green_time = {}

    for road, value in road_pcu.items():
        if total == 0:
            time = MIN_TIME
        else:
            time = max((value / total) * cycle_time, MIN_TIME)

        green_time[road] = round(time)

    return green_time


# ---------------- MAIN ---------------- #
def main():
    model = YOLO("yolov8n.pt")

    road_pcu = get_multi_road_pcu(model)
    green_time = calculate_signal_from_roads(road_pcu)

    print("Road PCU:", road_pcu)
    print("Signal Timing:", green_time)


if __name__ == "__main__":
    main()

def calculate_signal(total_pcu):
    cycle_time = 120
    MIN_TIME = 10

    road_pcu = {
        "A": total_pcu * 0.5,
        "B": total_pcu * 0.3,
        "C": total_pcu * 0.15,
        "D": total_pcu * 0.05
    }

    total = sum(road_pcu.values())
    green_time = {}

    for road, value in road_pcu.items():
        if total == 0:
            time = MIN_TIME
        else:
            time = max((value / total) * cycle_time, MIN_TIME)

        green_time[road] = round(time)

    return green_time