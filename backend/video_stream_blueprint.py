# Dette skriptet starter videostreamen fra video_stream.py

# Importerer nødvendige biblioteker
from flask import Blueprint, Response
import subprocess
import threading
import time

def discard_stderr(stream):
    for line in iter(stream.readline, b''):
        print("[stderr]", line.decode(errors="ignore").strip())

# Lager en flask blueprint for videostreamen
video_stream_bp = Blueprint('video_stream_bp', __name__)

# Funksjon for å hente bilder fra video_stream.py og sender dem til nettleseren
def generate_frames():
    # Starter video_stream.py som en egen prosess
    process = subprocess.Popen(
        ['python3', 'video_stream.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0 # Sikrer at vi får sanntidsdata
    )

    threading.Thread(target=discard_stderr, args=(process.stderr,), daemon=True).start()

    buffer = b""
    frame_marker = b"--FRAME--\n"

    try:
        while True:
            # Leser data fra prosessen
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            buffer += chunk

            while frame_marker in buffer:
                marker_index = buffer.find(frame_marker)
                frame_data = buffer[:marker_index]
                buffer = buffer[marker_index + len(frame_marker):]

                # Hvis har et bilde, konverterer det til riktig format og sender det
                if frame_data:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' +
                           frame_data + b'\r\n')
    finally:
        # Stopp prosessen når streamen er ferdig 
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

# Viser videoen i nettleseren når bruker besøker livestream i nettleser
@video_stream_bp.route('/live-camera-feed')
def live_camera_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')