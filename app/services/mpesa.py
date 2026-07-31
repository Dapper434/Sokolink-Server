import os
import base64
import threading
import time
from datetime import datetime
import requests
from app.extensions import db
from app.models.order import Order


CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'mock_consumer_key')
CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'mock_consumer_secret')
SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
PASSKEY = os.environ.get('MPESA_PASSKEY', 'mock_passkey')
CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://mydomain.com/orders/mpesa-callback')

def simulate_mpesa_callback(order_id, phone_number):
    # Fake successful payment for local testing
    def task():
        time.sleep(3)
        from wsgi import app
        with app.app_context():
            order = Order.query.get(order_id)
            if order:
                order.status = 'paid'
                order.phone_number = phone_number
                order.mpesa_receipt_number = f"MOCK{int(time.time())}"
                db.session.commit()

    threading.Thread(target=task).start()


