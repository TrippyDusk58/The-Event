import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import json
from datetime import datetime
import base64


# Get Access Token
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json().get("access_token")


# STK Push Request
def stk_push(phone_number, amount):
    access_token = get_access_token()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://darajambili.heroku.com/express-payment",
        "AccountReference": "EventTicket",
        "TransactionDesc": "Ticket Purchase"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Generate Password for STK Push
def generate_password():
    passkey = settings.MPESA_PASSKEY
    shortcode = settings.MPESA_SHORTCODE
    timestamp = get_timestamp()
    data_to_encode = f"{shortcode}{passkey}{timestamp}".encode("utf-8")
    return base64.b64encode(data_to_encode).decode("utf-8")

# Generate Timestamp
def get_timestamp():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S")
