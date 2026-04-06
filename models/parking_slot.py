from models import db


class ParkingSlot(db.Model):
    """A single parking slot on campus."""
    __tablename__ = 'parking_slots'

    slot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slot_location = db.Column(db.String(100), nullable=False)
    slot_status = db.Column(db.String(20), nullable=False, default='Available', index=True)  # Available / Occupied
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    reservations = db.relationship('Reservation', backref='slot', lazy=True)

    def __repr__(self):
        return f'<Slot {self.slot_id} @ {self.slot_location} [{self.slot_status}]>'
