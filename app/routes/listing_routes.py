from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.listing import Listing
from app.models.user import User

listing_bp = Blueprint('listings', __name__)

def listing_json(listing):
    return {
        "id": listing.id,
        "farmer_id": listing.farmer_id,
        "farmer_name": listing.farmer.name,
        "crop_name": listing.crop_name,
        "quantity_kg": listing.quantity_kg,
        "price_per_kg": listing.price_per_kg
    }

@listing_bp.route('', methods=['GET'])
def get_listings():
    listings = Listing.query.all()
    return jsonify([listing_json(l) for l in listings]), 200    


@listing_bp.route('/<int:id>', methods=['GET'])
def get_listing(id):
    return jsonify(listing_json(Listing.query.get_or_404(id))), 200


@listing_bp.route('', methods=['POST'])
@jwt_required()
def create_listing():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'farmer':
        return jsonify({"message": "Only farmers can create listings"}), 403 

     
    data = request.get_json()
    if not data or not all(k in data for k in ("crop_name", "quantity_kg", "price_per_kg")):
        return jsonify({"message": "Missing required fields"}), 400    

    listing = Listing(
        farmer_id=user_id,
        crop_name=data["crop_name"],
        quantity_kg=data["quantity_kg"],
        price_per_kg=data["price_per_kg"]    
    )   






