import sys
import json
from ultralytics import YOLO

# Laster inn ai-modellen
model = YOLO("/home/pi/yolo-env/yolov8n.pt")

# Filbanen
image_path = sys.argv[1]

# Kjør prediksjon med modellen på bildet
results = model(image_path)

# Samle detekterte objekter for notifications
detections = []

for result in results:
    for cls, conf in zip(result.boxes.cls, result.boxes.conf):
        name = model.names[int(cls)]
        confidence = conf.item()
        if name in ["person", "cat", "dog", "robot"]:
            detections.append(f"{name} ({confidence:.2f})")

# JSON print
print(json.dumps(detections))