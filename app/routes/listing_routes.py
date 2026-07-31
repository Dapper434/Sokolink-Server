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
