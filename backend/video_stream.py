# Dette skriptet tar bilder fra Rasperry Pi-kamerat 
# og sender dem som en videostream

# Importerer nødvendige biblioteker
from picamera2 import Picamera2
import cv2
import sys
import time

# Initialiserer Picamera2 og konfigurerer videostreamen
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2) # Ventetid for å sikre at kameraet er klart

try:
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        # Gjør om bildet til bytes
        frame_bytes = buffer.tobytes()

        # Skriv ut bildet og marker starten på nytt bilde
        sys.stdout.buffer.write(b"--FRAME--\n")
        sys.stdout.buffer.write(frame_bytes)
        sys.stdout.buffer.write(b"\n") 
        sys.stdout.flush()
        
        # Begrens hastigheten til ca. 20 FPS
        time.sleep(0.05)
except KeyboardInterrupt:
    # Stopper kameraet ved avbrudd
    picam2.stop()