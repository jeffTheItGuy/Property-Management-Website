import os
import requests
from app.config import settings


def send_sms(phone: str, message: str) -> bool:
    """Send SMS via Africa's Talking or mock in dev.
    
    In production, configure SMS_API_KEY and SMS_PROVIDER.
    In development, prints to stdout and returns True.
    """
    if not settings.SMS_API_KEY or settings.SMS_API_KEY == "your_sms_api_key":
        print(f"[DEV SMS] To: {phone} | Message: {message}")
        return True

    if settings.SMS_PROVIDER == "africas_talking":
        return _send_africas_talking(phone, message)

    # Fallback: mock
    print(f"[SMS] To: {phone} | Message: {message}")
    return True


def _send_africas_talking(phone: str, message: str) -> bool:
    """Africa's Talking SMS gateway."""
    try:
        url = "https://api.africastalking.com/version1/messaging"
        headers = {"apiKey": settings.SMS_API_KEY, "Accept": "application/json"}
        data = {
            "username": settings.SMS_SENDER_ID,
            "to": phone,
            "message": message,
            "from": settings.SMS_SENDER_ID,
        }
        resp = requests.post(url, data=data, headers=headers, timeout=30)
        return resp.status_code == 201
    except Exception as e:
        print(f"SMS send failed: {e}")
        return False
