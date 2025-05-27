import json
from pywebpush import webpush, WebPushException
from notifications import get_subscriptions

VAPID_PRIVATE_KEY = "2Ww_0Li10yL2K40vlRi9-fYUfI1M3mGHNxrLa13HTBw"
VAPID_CLAIMS = {"sub": "mailto:you@sayver.org"}

def send_notification(notification_type, extra_data=None):
    title = "Sayver Notification"
    body = "Default body"
    url = "https://sayver.org/dashboard.html"

    # Tilpasser tittel og melding basert på type
    if notification_type == "motion_detected":
        title = "Bevegelse oppdaget!"
        body = "PIR-sensoren registrerte bevegelse nå!"
    elif notification_type == "ai_detection":
        detected_items = ", ".join(extra_data.get("detected_items", [])) if extra_data else "Objekter oppdaget"
        title = "AI Deteksjon"
        body = f"Gjenkjente: {detected_items}"
    elif notification_type == "camera_error":
        title = "Kamera Feil"
        body = "Kunne ikke starte kameraet."
    elif notification_type == "custom":
        title = extra_data.get("title", "Custom Notification")
        body = extra_data.get("body", "Custom Body")

    # Send varsliner til alle abonnementer
    for sub in get_subscriptions():
        try:
            webpush(
                subscription_info=sub,
                data=json.dumps({
                    "title": title,
                    "body": body,
                    "url": url
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
            print(f"Push sendt: {title} -> {sub.get('endpoint')}")
        except WebPushException as e:
            print(f"Push-feil til {sub.get('endpoint')}: {e}")
            if e.response:
                print(f"?? HTTP Status: {e.response.status_code}")
                print(f"?? Response body: {e.response.text}")