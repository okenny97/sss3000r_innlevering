from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Definerer bruker tabellen
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    twofa_method = db.Column(db.String(20), default='totp')
    twofa_secret = db.Column(db.String(64), nullable=True)
    pending_twofa_secret = db.Column(db.String(64))

    def is_active(self):
        return True