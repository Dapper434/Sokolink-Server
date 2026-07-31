from app.extensions import db

class OrderItem(db.Model):    
   id = db.Column(db.Integer, primary_key=True)
   order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
   listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)