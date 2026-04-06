"""
Campus Parking Slot Management System (CPSMS)
Main Flask application entry point.
"""
from flask import Flask
from config import Config
from models import db
from models.user import bcrypt

# Import blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.staff import staff_bp


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 60)
    print("  CPSMS – Campus Parking Slot Management System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 60)
    print("\n  Default login credentials:")
    print("  Admin    → admin@campus.edu / admin123")
    print("  Student  → john@campus.edu  / student123")
    print("  Staff    → guard@campus.edu / staff123")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
