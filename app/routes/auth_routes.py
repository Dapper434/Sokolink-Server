from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Email already registered"}), 400

         # Store a hashed password, never plain text
    user = User(
        name=data.get('name'),
        email=data.get('email'),
        password_hash=generate_password_hash(data.get('password')),
        role=data.get('role', 'buyer')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201



@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()


    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"message": "Invalid credentials"}), 401



