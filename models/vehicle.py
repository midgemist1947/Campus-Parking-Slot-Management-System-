from models import db


class Vehicle(db.Model):
    """Vehicle registered by a user."""
    __tablename__ = 'vehicles'

    vehicle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    vehicle_number = db.Column(db.String(20), nullable=False, unique=True)
    vehicle_type = db.Column(db.String(30), nullable=False)  # car / bike / scooter / etc.

    reservations = db.relationship('Reservation', backref='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.vehicle_number} ({self.vehicle_type})>'
