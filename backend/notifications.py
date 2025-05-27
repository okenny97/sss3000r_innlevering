from flask import Blueprint
import os
import json
import threading

notifications_bp = Blueprint('notifications', __name__)
subscriptions_file = "subscriptions.json"
file_lock = threading.Lock()

# Thread-safe lasting av subscriptions
def load_subscriptions():
    if os.path.exists(subscriptions_file):
        with file_lock:
            try:
                with open(subscriptions_file, "r") as f:
                    subs = json.load(f)

                # Fjern duplikater
                seen = {}
                for sub in subs:
                    seen[sub.get("endpoint")] = sub
                unique_subs = list(seen.values())

                # Lagre om duplikater er funnet
                if len(unique_subs) != len(subs):
                    with open(subscriptions_file, "w") as f:
                        json.dump(unique_subs, f, indent=2)
                        print("? Duplikater fjernet fra subscriptions.json")

                return unique_subs

            except json.JSONDecodeError:
                print("? subscriptions.json er korrupt. Returnerer tom liste.")
                return []
    return []


# Lagrer
def save_subscriptions(subscriptions):
    with file_lock:
        try:
            with open(subscriptions_file, "w") as f:
                json.dump(subscriptions, f, indent=2)
        except Exception as e:
            print(f"? Klarte ikke lagre subscriptions: {e}")

# Hente alle subscriptions
def get_subscriptions():
    return load_subscriptions()

# Legge til subscription
def add_subscription(data):
    subscriptions = load_subscriptions()

    # Fjern eksisterende entry med samme endpoint
    subscriptions = [sub for sub in subscriptions if sub.get("endpoint") != data.get("endpoint")]

    # Legg til
    subscriptions.append(data)

    save_subscriptions(subscriptions)