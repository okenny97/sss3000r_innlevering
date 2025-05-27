import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json
from notifications import get_subscriptions
from pywebpush import webpush, WebPushException

# Sett opp GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN = 4
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Sett opp kamera
picam2 = Picamera2()
image_folder = "/var/www/html/media/pictures/"
video_folder = "/var/www/html/media/video/"

print("? PIR Sensor aktivert ? Venter paa bevegelse...")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("? Bevegelse oppdaget")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            date_folder = datetime.now().strftime("%Y-%m-%d")
            image_dir = Path(image_folder) / date_folder
            video_dir = Path(video_folder) / date_folder
            image_dir.mkdir(parents=True, exist_ok=True)
            video_dir.mkdir(parents=True, exist_ok=True)

            image_path = image_dir / f"motion_{timestamp}.jpg"
            video_path = video_dir / f"motion_{timestamp}.mp4"

            # Ta bilde
            picam2.configure(picam2.create_still_configuration())
            picam2.start()
            time.sleep(2)
            picam2.capture_file(str(image_path))
            picam2.stop()
            print(f"? Bilde lagret: {image_path}")

            # Kjør AI
            result = subprocess.run(
                ["/home/pi/yolo-env/bin/python3", "/home/pi/flask_app/ai.py", str(image_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                try:
                    detection_list = json.loads(result.stdout)
                    if detection_list:
                        message = ", ".join(detection_list)

                        # Send notification
                        for sub in get_subscriptions():
                            print("? Sender notification til:", sub.get("endpoint"))
                            try:
                                webpush(
                                    subscription_info=sub,
                                    data=json.dumps({
                                        "title": "Video: Deteksjon oppdaget",
                                        "body": f"AI gjenkjente: {message}",
                                        "url": "https://sayver.org/dashboard.html"
                                    }),
                                    vapid_private_key="2Ww_0Li10yL2K40vlRi9-fYUfI1M3mGHNxrLa13HTBw",
                                    vapid_claims={"sub": "mailto:you@sayver.org"}
                                )
                                print("? Push sendt")
                            except WebPushException as e:
                                print("? Push-feil:", e)
                                if e.response:
                                    print("?? HTTP Status:", e.response.status_code)
                                    print("?? Response body:", e.response.text)
                    else:
                        print("?? Ingen interessante objekter funnet.")
                except json.JSONDecodeError:
                    print("?? Kunne ikke lese AI-resultatene.")
            else:
                print("?? Feil ved kjoring av AI.")

            # Start videoopptak
            print(f"? Starter videoopptak: {video_path}")
            picam2.configure(picam2.create_video_configuration())
            encoder = H264Encoder()
            output = FfmpegOutput(str(video_path))
            picam2.start_recording(encoder, output)

            start_time = datetime.now()
            max_duration = timedelta(seconds=10)

            while GPIO.input(PIR_PIN) or (datetime.now() - start_time < max_duration):
                if datetime.now() - start_time > max_duration:
                    print("? Maks videoopptakstid naadd (10 sekunder).")
                    break
                time.sleep(1)

            picam2.stop_recording()
            print(f"? Video lagret: {video_path}")

            print("? 30s cooldown...")
            time.sleep(30)

            while GPIO.input(PIR_PIN):
                time.sleep(0.1)
            print("? Klar for ny deteksjon.")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n? Avslutter...")
    GPIO.cleanup()
    print("GPIO nullstilt")