from flask import Flask
from config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.listing_routes import listing_bp
    from app.routes.order_routes import order_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(listing_bp, url_prefix='/api/listings')
    app.register_blueprint(order_bp, url_prefix='/api/orders')

    # Create tables if they don't exist
    with app.app_context():
        from app.models import user, listing, order, order_item  # noqa: F811
        db.create_all()

    return app
