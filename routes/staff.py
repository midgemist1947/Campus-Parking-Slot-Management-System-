from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
from models import db
from models.reservation import Reservation
from models.user import User
from models.vehicle import Vehicle
from models.parking_slot import ParkingSlot
from utils.decorators import staff_required

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/dashboard')
@staff_required
def dashboard():
    """Staff monitoring dashboard – read-only."""
    active_reservations = db.session.query(
        Reservation, User, Vehicle, ParkingSlot
    ).join(User, Reservation.user_id == User.user_id
    ).join(Vehicle, Reservation.vehicle_id == Vehicle.vehicle_id
    ).join(ParkingSlot, Reservation.slot_id == ParkingSlot.slot_id
    ).filter(Reservation.is_active == True
    ).order_by(Reservation.created_at.desc()).all()

    return render_template('dashboard/staff.html', reservations=active_reservations)


@staff_bp.route('/api/search')
@staff_required
def search_vehicle():
    """Search reservations by vehicle number."""
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])

    results = db.session.query(
        Reservation, User, Vehicle, ParkingSlot
    ).join(User, Reservation.user_id == User.user_id
    ).join(Vehicle, Reservation.vehicle_id == Vehicle.vehicle_id
    ).join(ParkingSlot, Reservation.slot_id == ParkingSlot.slot_id
    ).filter(
        Vehicle.vehicle_number.ilike(f'%{query}%'),
        Reservation.is_active == True
    ).all()

    return jsonify([{
        'reservation_id': r.reservation_id,
        'user_name': u.user_name,
        'email': u.email,
        'vehicle_number': v.vehicle_number,
        'vehicle_type': v.vehicle_type,
        'slot_location': s.slot_location,
        'reservation_date': r.reservation_date.isoformat(),
        'reservation_time': str(r.reservation_time),
    } for r, u, v, s in results])
