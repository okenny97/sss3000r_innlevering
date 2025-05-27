from flask import Blueprint, request, jsonify
import subprocess
from pathlib import Path

start_alarm_bp = Blueprint("start_alarm_bp", __name__)

@start_alarm_bp.route("/start-alarm", methods=["POST"])
def start_alarm():
    data = request.get_json()
    alarm_type = data.get("type", "video")
    base_path = Path("/home/pi/flask_app")

    script = base_path / ("pir_picture.py" if alarm_type == "image" else "pir_video.py")

    try:
        subprocess.Popen(["/usr/bin/python3", str(script)])
        return jsonify({"status": f"{alarm_type}-alarm aktivert"})
    except Exception as e:
        return jsonify({"status": "Feil", "error": str(e)}), 500