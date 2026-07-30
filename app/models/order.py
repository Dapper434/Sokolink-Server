from app.extensions import db
from datetime import datetime, timezone

class Order(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('used.id'), nullable=False)