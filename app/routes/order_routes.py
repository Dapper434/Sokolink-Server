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
    if user.role != 'buyer':
        return jsonify({"message": "Only buyers can place orders"}), 403

    
    data = request.get_json()
    if not data or "items" not in data or not isinstance(data["items"], list):
        return jsonify({"message": "Invalid payload"}), 400

    phone_number = data.get("phone_number")
    if not phone_number:
        return jsonify({"message": "Phone number is required for payment"}), 400    

    order = Order(buyer_id=user_id, status='pending', phone_number=phone_number)
    db.session.add(order)
    db.session.flush()

    total_amount = 0
    for item in data["items"]:
        listing = Listing.query.get(item["listing_id"])
        if not listing:
            db.session.rollback()
            return jsonify({"message": f"Listing {item['listing_id']} not found"}), 404
        if listing.quantity_kg < item["quantity_kg"]:
            db.session.rollback()
            return jsonify({"message": f"Insufficient quantity for {listing.crop_name}"}), 400

        listing.quantity_kg -= item["quantity_kg"]
        qty = item["quantity_kg"]
        total_amount += listing.price_per_kg * qty

        db.session.add(OrderItem(
            order_id=order.id,
            listing_id=listing.id,
            quantity_kg=qty,
            price_at_order=listing.price_per_kg
        ))

    order.total_amount = total_amount
    db.session.commit()    
