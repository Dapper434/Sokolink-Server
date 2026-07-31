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

