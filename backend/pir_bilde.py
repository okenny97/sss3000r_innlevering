import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
from datetime import datetime
from pathlib import Path
import subprocess
import json
from notifications_melding import send_notification

# Sett opp GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN = 4
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Sett opp kamera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

# Mapper
image_folder = "/var/www/html/media/pictures/"

print("? PIR Sensor aktivert ? Venter på bevegelse...")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("? Bevegelse oppdaget")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            date_folder = datetime.now().strftime("%Y-%m-%d")
            full_folder_path = Path(image_folder) / date_folder
            full_folder_path.mkdir(parents=True, exist_ok=True)

            image_path = full_folder_path / f"motion_{timestamp}.jpg"

            print(f"? Tar bilde: {image_path}")
            picam2.start()
            time.sleep(2)
            picam2.capture_file(str(image_path))
            picam2.stop()
            print(f"? Bilde lagret: {image_path}")

            # Send detksjon på bevegelse notification
            send_notification("motion_detected", {"image_path": str(image_path)})

            # Kjør AI på bildet
            result = subprocess.run(
                ["/home/pi/yolo-env/bin/python3", "/home/pi/flask_app/ai.py", str(image_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("? AI-output mottatt.")
                lines = result.stdout.strip().split("\n")
                if lines:
                    last_line = lines[-1]
                    try:
                        detection_list = json.loads(last_line)
                        if detection_list:
                            print(f"? AI gjenkjente: {', '.join(detection_list)}")
                            send_notification("ai_detection", {"detected_items": detection_list})
                        else:
                            print("?? Ingen interessante objekter funnet.")
                    except json.JSONDecodeError:
                        print("? FEIL: Kunne ikke lese siste AI-resultat som JSON.")
                else:
                    print("? Ingen output fra AI.")
            else:
                print("? FEIL: ai.py kjorte ikke riktig.")

            # Cooldown for å unngå trøbbel med pir
            print("? 30s cooldown...")
            time.sleep(30)

            # Vent til bevegelse er borte
            while GPIO.input(PIR_PIN):
                time.sleep(0.1)
            print("? Klar for ny deteksjon.")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n? Avslutter...")
    GPIO.cleanup()
    print("GPIO nullstilt")