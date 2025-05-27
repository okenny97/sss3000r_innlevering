from server import db, app

# Blir brukt til å opprette databasen og tabellene
with app.app_context():
    db.create_all()

print("Databasen ble opprettet")
exit()