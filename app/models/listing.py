 from app.extensions import db

 class Listing(db.model):
     id = db.Column(db.Integer, primary_key= True)
     
