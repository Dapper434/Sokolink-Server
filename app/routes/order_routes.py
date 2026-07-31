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

    try:
        mpesa_res = initiate_stk_push(phone_number, total_amount, order.id)
        if mpesa_res.get('ResponseCode') != '0':
            return jsonify({"message": "STK Push failed", "details": mpesa_res}), 500
    except Exception as e:
        return jsonify({"message": "Failed to initiate payment", "error": str(e)}), 500

    return jsonify({
        "id": order.id,
        "total_amount": total_amount,
        "status": order.status,
        "message": "Order created and payment prompt sent to your phone."
    }), 201 

@order_bp.route('/mpesa-callback', methods=['POST'])
def mpesa_callback():
    # Safaricom calls this after the user pays on their phone
    data = request.get_json()
    if not data:
        return jsonify({"ResultCode": 1, "ResultDesc": "Invalid payload"}), 400

    callback = data.get("Body", {}).get("stkCallback", {})
    if callback.get("ResultCode") == 0:
        items = callback.get("CallbackMetadata", {}).get("Item", [])
        receipt = next((i["Value"] for i in items if i["Name"] == "MpesaReceiptNumber"), None)
        phone = next((i["Value"] for i in items if i["Name"] == "PhoneNumber"), None)
        print(f"Payment successful: {receipt} by {phone}")
    else:
        print(f"Payment failed: {callback.get('ResultDesc')}")

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

    
@order_bp.route('', methods=['GET'])
@jwt_required()
def list_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role == 'buyer':
        orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.join(OrderItem).join(Listing).filter(
            Listing.farmer_id == user_id
        ).order_by(Order.order_date.desc()).all()
        orders = sorted(set(orders), key=lambda o: o.order_date, reverse=True)

    return jsonify([order_json(o) for o in orders]), 200
   


@order_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(id):
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(id)   