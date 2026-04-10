# signal_logic.py

# PCU values for each road (example)
pcu = {
    "A": 4,
    "B": 2,
    "C": 1,
    "D": 0
}

# total signal cycle time (seconds)
cycle_time = 120

# minimum green time
MIN_TIME = 10

# calculate total PCU
total_pcu = sum(pcu.values())

green_time = {}

for road, value in pcu.items():
    if total_pcu == 0:
        time = MIN_TIME
    else:
        time = (value / total_pcu) * cycle_time
        time = max(time, MIN_TIME)

    green_time[road] = round(time)

# print result
print("\n--- Signal Timing ---")
for road in green_time:
    print(f"Road {road} → Green: {green_time[road]} sec")