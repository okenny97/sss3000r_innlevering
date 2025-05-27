from flask import Blueprint, request, jsonify
import subprocess
import threading
import os
import signal
import json
from pywebpush import webpush, WebPushException
from notifications import add_subscription, get_subscriptions
from send_mail import send_alarm_email

notifications_bp = Blueprint('notifications_bp', __name__)
pir_process = None

settings_file = "system_settings.json"
settings_lock = threading.Lock()

@notifications_bp.route("/load-settings", methods=["GET"])
def load_settings():
    try:
        settings = load_system_settings()
        return jsonify(settings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_system_settings():
    if os.path.exists(settings_file):
        with settings_lock:
            try:
                with open(settings_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_system_settings(settings):
    with settings_lock:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

# Web Push notifications konfigurasjon
VAPID_PRIVATE_KEY = "2Ww_0Li10yL2K40vlRi9-fYUfI1M3mGHNxrLa13HTBw"
VAPID_CLAIMS = {"sub": "mailto:you@sayver.org"}

@notifications_bp.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        subscription = request.get_json()
        add_subscription(subscription)
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route("/save-settings", methods=["POST"])
def save_settings():
    try:
        settings = request.get_json()
        save_system_settings(settings)
        return jsonify({"message": "Settings saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route("/send-notification", methods=["POST"])
def send_notification():
    data = request.get_json()
    for sub in get_subscriptions()[:]:
        try:
            webpush(
                subscription_info=sub,
                data=json.dumps({
                    "title": data.get('title', 'Notification'),
                    "body": data.get('body', 'Hello from Sayver!'),
                    "url": data.get('url', 'https://sayver.org/dashboard.html')
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except WebPushException as e:
            if e.response and e.response.status_code in [404, 410]:
                subs = [s for s in get_subscriptions() if s.get("endpoint") != sub.get("endpoint")]
                from notifications import save_subscriptions
                save_subscriptions(subs)
    return jsonify({"sent": True})

# PIR script for klontroll av pir
@notifications_bp.route("/run-pir", methods=["POST"])
def run_pir():
    global pir_process
    try:
        if pir_process and pir_process.poll() is None:
            return jsonify({"message": "Already running"}), 200

        settings = load_system_settings()
        mode = settings.get("alarmMode", "bilde")
        script = "pir_video.py" if mode == "video" else "pir_bilde.py"

        logfile = open("/home/pi/flask_app/pir_bilde_log.txt", "a")
        pir_process = subprocess.Popen(
            ["/usr/bin/python3", script],
            stdout=logfile,
            stderr=logfile,
            start_new_session=True
        )

        # Send e-post hvis aktivert
        if settings.get("emailNotifications", False):
            send_alarm_email("Alarm utløst!", "PIR-sensoren har registrert bevegelse.")

        return jsonify({"message": f"{script} started"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route("/stop-pir", methods=["POST"])
def stop_pir():
    try:
        result = subprocess.run(["pgrep", "-f", "pir_.*\\.py"], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                os.kill(int(pid), signal.SIGTERM)
            return jsonify({"message": "PIR script stopped"}), 200
        else:
            return jsonify({"message": "No PIR script running"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route("/status-pir", methods=["GET"])
def status_pir():
    try:
        result = subprocess.run(["pgrep", "-f", "pir_.*\\.py"], capture_output=True, text=True)
        return jsonify({"status": "running" if result.returncode == 0 else "stopped"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500