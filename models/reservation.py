from models import db
from datetime import datetime, date, time as dt_time


class Reservation(db.Model):
    """A parking reservation linking user, vehicle, and slot."""
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slots.slot_id'), nullable=False, index=True)
    reservation_date = db.Column(db.Date, nullable=False, default=date.today)
    reservation_time = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time())
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation {self.reservation_id} User={self.user_id} Slot={self.slot_id}>'
