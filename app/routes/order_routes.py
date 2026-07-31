from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.listing import Listing
from app.models.user import User
from app.services.mpesa import initiate_stk_push

order_bp = Blueprint('orders', __name__)
