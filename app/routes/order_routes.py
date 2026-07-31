from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.listing import Listing
from app.models.user import User
from app.services.mpesa import initiate_stk_push

order_bp = Blueprint('orders', __name__)

def order_json(order):
    return {
        "id": order.id,
        "buyer_name": order.buyer.name,
        "status": order.status,
        "total_amount": order.total_amount,
        "order_date": order.order_date.isoformat(),
        "phone_number": order.phone_number,
        "mpesa_receipt_number": order.mpesa_receipt_number,
        "items": [{
            "listing_id": item.listing_id,
            "crop_name": item.listing.crop_name,
            "quantity_kg": item.quantity_kg,
            "price_at_order": item.price_at_order
        } for item in order.items]
    }

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
