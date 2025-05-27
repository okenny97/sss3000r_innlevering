from flask import Flask
from werkzeug.security import generate_password_hash
from database import db, User
import os

# Blir brukt til å opprette brukere, spesielt den første brukeren
# Siden man kan opprette nye brukere via brukergrensesnittet når man er logget inn

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "instance", "app.db"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'temporarysecret'

db.init_app(app)

with app.app_context():
    db.create_all()

    if User.query.filter_by(username="user").first():
        print("Brukeren finnes allerede")
    else:
        password = "admin123"
        hashed_password = generate_password_hash(password)

        user = User(username="user", email="user@eksample.com", password=hashed_password)
        db.session.add(user)
        db.session.commit()

        print("Opprettet bruker")
        print(f"Brukernavn: user\nPassord: {password}")