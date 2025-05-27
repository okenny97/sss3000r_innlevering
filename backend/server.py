import os
import subprocess
import threading
import time
import json
import importlib
import traceback
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from auth import auth_bp
from database import db, User
from werkzeug.middleware.proxy_fix import ProxyFix
from pywebpush import webpush, WebPushException
from flask import jsonify

# Per nå har vi satt opp server.py som kjører flask-applikasjonen, på en måte som gjør at hvis
# hvis en blueprint ikke fungerer, så vil den ikke krasje hele applikasjonen under produksjon.
# Derfor har vi kommentert ut blueprints og imports.

#from notifications_blueprint import notifications_bp
#from read_temp_blueprint import temperature_bp
#from video_stream_blueprint import video_stream_bp
#from test_livestream import video_stream_bp
#from start_alarm_blueprint import start_alarm_bp

# Flask app
app = Flask(__name__)

# SQLite database
os.makedirs(os.path.join(app.instance_path), exist_ok=True)
db_path = os.path.join(app.instance_path, "app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "anothersecretkey"
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
app.config["SERVER_NAME"] = None

db.init_app(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Funksjon for å registrere blueprints på en sikker måte, slik at hvis en blueprint ikke fungerer, 
# så vil den ikke krasje hele applikasjonen.
def safe_register(bp_name, module_path, attr_name, url_prefix="/api"):
    try:
        module = importlib.import_module(module_path)
        blueprint = getattr(module, attr_name)
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        print(f"Fungerer - Registeret blueprint: {bp_name}")
    except Exception as e:
        print(f"ERROR - Feilet med å laste inn blueprint '{bp_name}': {e}")
        print(traceback.format_exc())

# Registrerer blueprints
safe_register("auth", "auth", "auth_bp")
safe_register("notifications", "notifications_blueprint", "notifications_bp")
safe_register("temperature", "read_temp_blueprint", "temperature_bp")
safe_register("video_stream", "video_stream_blueprint", "video_stream_bp")
safe_register("start_alarm", "start_alarm_blueprint", "start_alarm_bp")

# Registrerer blueprints (kommentert ut for å unngå krasj under produksjon)
# Registrerer auth blueprint
#app.register_blueprint(auth_bp, url_prefix='/api')

# Registrerer notification blueprint
#app.register_blueprint(notifications_bp, url_prefix="/api")

# Registrerer temperature blueprint
#app.register_blueprint(temperature_bp, url_prefix='/api')

# Registrerer video stream blueprint
#app.register_blueprint(video_stream_bp, url_prefix='/api')

# Registrerer start alarm blueprint
#app.register_blueprint(start_alarm_bp, url_prefix='/api')

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.before_request
def before_request():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return redirect(request.url.replace("http://", "https://"), code=301)
    print(f"Innkommende forespørsel: {request.method} {request.url}")

with app.app_context():
    db.create_all()

@app.route("/api/status", methods=["GET"])
def server_status():
    return jsonify({"status": "Serveren fungerer!"}), 200

# Starter Flask-applikasjonen
if __name__ != "__main__":
    application = app  # Blir kjørt med gunicorn