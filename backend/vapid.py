from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Genererer VAPID nøkler til å bruke med push-varsler i Flask
# Generer en ny EC (elliptic curve) privat nøkkel
private_key = ec.generate_private_key(ec.SECP256R1())

# Hent den private nøkkelen i PEM-format
pem_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Hent den offentlige nøkkelen i ukomprimert format (bytes)
public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Enkoder den offentlige nøkkelen i URL-sikker base64-format
vapid_public_key = base64.urlsafe_b64encode(public_key).decode('utf-8').rstrip("=")

# Enkoder den private nøkkelen i PEM-format for Flask-server bruk
vapid_private_key = base64.urlsafe_b64encode(
    private_key.private_numbers().private_value.to_bytes(32, "big")
).decode('utf-8').rstrip("=")

print("Offentlig VAPID key (For JS (frontend)):", vapid_public_key)
print("Privat VAPID key (For Flask (backend)):", vapid_private_key)