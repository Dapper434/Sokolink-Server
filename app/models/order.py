from app.extensions import db
from datetime import datetime, timezone

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending') # pending, confirmed, fulfilled, cancelled, paid, failed
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    
    phone_number = db.Column(db.String(20), nullable=True)
    mpesa_receipt_number = db.Column(db.String(50), nullable=True)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
