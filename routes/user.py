from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.parking_slot import ParkingSlot
from models.reservation import Reservation
from utils.decorators import login_required
from datetime import datetime, date

user_bp = Blueprint('user', __name__, url_prefix='/user')


# ── Dashboard ────────────────────────────────────────────────────────────────

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """Main user dashboard."""
    user_id = session['user_id']
    active_reservation = Reservation.query.filter_by(user_id=user_id, is_active=True).first()
    vehicles = Vehicle.query.filter_by(user_id=user_id).all()
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    return render_template('dashboard/user.html',
                           active_reservation=active_reservation,
                           vehicles=vehicles,
                           reservations=reservations)


# ── Parking Slots (AJAX) ────────────────────────────────────────────────────

@user_bp.route('/api/slots')
@login_required
def api_slots():
    """Return all active slots as JSON for live grid updates."""
    location_filter = request.args.get('location', '').strip()
    query = ParkingSlot.query.filter_by(is_active=True)
    if location_filter:
        query = query.filter(ParkingSlot.slot_location.ilike(f'%{location_filter}%'))
    slots = query.order_by(ParkingSlot.slot_id).all()
    return jsonify([{
        'slot_id': s.slot_id,
        'slot_location': s.slot_location,
        'slot_status': s.slot_status,
    } for s in slots])


# ── Reserve Slot ─────────────────────────────────────────────────────────────

@user_bp.route('/reserve', methods=['POST'])
@login_required
def reserve_slot():
    """Reserve a parking slot with transaction safety."""
    user_id = session['user_id']
    slot_id = request.form.get('slot_id', type=int)
    vehicle_id = request.form.get('vehicle_id', type=int)

    if not slot_id or not vehicle_id:
        flash('Please select a slot and a vehicle.', 'danger')
        return redirect(url_for('user.dashboard'))

    # Verify vehicle belongs to user
    vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id, user_id=user_id).first()
    if not vehicle:
        flash('Invalid vehicle selection.', 'danger')
        return redirect(url_for('user.dashboard'))

    try:
        # ── Begin transaction ────────────────────────────────────────
        # 1. Check if user already has an active reservation
        existing = Reservation.query.filter_by(user_id=user_id, is_active=True).first()
        if existing:
            flash('You already have an active reservation. Cancel it first to book a new one.', 'warning')
            return redirect(url_for('user.dashboard'))

        # 2. Re-check slot availability (prevent race condition)
        slot = db.session.query(ParkingSlot).filter_by(
            slot_id=slot_id, slot_status='Available', is_active=True
        ).with_for_update().first()

        if not slot:
            flash('This slot is no longer available. Please choose another.', 'danger')
            return redirect(url_for('user.dashboard'))

        # 3. Create reservation and update slot status
        reservation = Reservation(
            user_id=user_id,
            vehicle_id=vehicle_id,
            slot_id=slot_id,
            reservation_date=date.today(),
            reservation_time=datetime.now().time(),
            is_active=True
        )
        slot.slot_status = 'Occupied'

        db.session.add(reservation)
        db.session.commit()
        flash(f'Slot {slot.slot_location} reserved successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while booking. Please try again.', 'danger')

    return redirect(url_for('user.dashboard'))


# ── Cancel Reservation ───────────────────────────────────────────────────────

@user_bp.route('/cancel/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """Cancel an active reservation and free the slot."""
    user_id = session['user_id']
    reservation = Reservation.query.filter_by(
        reservation_id=reservation_id, user_id=user_id, is_active=True
    ).first()

    if not reservation:
        flash('Reservation not found or already cancelled.', 'warning')
        return redirect(url_for('user.dashboard'))

    try:
        reservation.is_active = False
        slot = ParkingSlot.query.get(reservation.slot_id)
        if slot:
            slot.slot_status = 'Available'
        db.session.commit()
        flash('Reservation cancelled successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error cancelling reservation.', 'danger')

    return redirect(url_for('user.dashboard'))


# ── Vehicle CRUD ─────────────────────────────────────────────────────────────

@user_bp.route('/vehicles')
@login_required
def vehicles():
    """List user's vehicles (JSON for AJAX)."""
    user_id = session['user_id']
    vlist = Vehicle.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'vehicle_id': v.vehicle_id,
        'vehicle_number': v.vehicle_number,
        'vehicle_type': v.vehicle_type,
    } for v in vlist])


@user_bp.route('/vehicle/add', methods=['POST'])
@login_required
def add_vehicle():
    """Add a new vehicle."""
    user_id = session['user_id']
    number = request.form.get('vehicle_number', '').strip().upper()
    vtype = request.form.get('vehicle_type', '').strip()

    if not number or not vtype:
        flash('Vehicle number and type are required.', 'danger')
        return redirect(url_for('user.dashboard'))

    if Vehicle.query.filter_by(vehicle_number=number).first():
        flash('This vehicle number is already registered.', 'warning')
        return redirect(url_for('user.dashboard'))

    vehicle = Vehicle(user_id=user_id, vehicle_number=number, vehicle_type=vtype)
    db.session.add(vehicle)
    db.session.commit()
    flash(f'Vehicle {number} added successfully.', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/vehicle/edit/<int:vehicle_id>', methods=['POST'])
@login_required
def edit_vehicle(vehicle_id):
    """Edit a vehicle."""
    user_id = session['user_id']
    vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id, user_id=user_id).first()
    if not vehicle:
        flash('Vehicle not found.', 'danger')
        return redirect(url_for('user.dashboard'))

    number = request.form.get('vehicle_number', '').strip().upper()
    vtype = request.form.get('vehicle_type', '').strip()

    if not number or not vtype:
        flash('Vehicle number and type are required.', 'danger')
        return redirect(url_for('user.dashboard'))

    dup = Vehicle.query.filter(Vehicle.vehicle_number == number, Vehicle.vehicle_id != vehicle_id).first()
    if dup:
        flash('This vehicle number is already registered to another record.', 'warning')
        return redirect(url_for('user.dashboard'))

    vehicle.vehicle_number = number
    vehicle.vehicle_type = vtype
    db.session.commit()
    flash('Vehicle updated.', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/vehicle/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    """Delete a vehicle (only if no active reservation uses it)."""
    user_id = session['user_id']
    vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id, user_id=user_id).first()
    if not vehicle:
        flash('Vehicle not found.', 'danger')
        return redirect(url_for('user.dashboard'))

    active = Reservation.query.filter_by(vehicle_id=vehicle_id, is_active=True).first()
    if active:
        flash('Cannot delete vehicle with an active reservation.', 'warning')
        return redirect(url_for('user.dashboard'))

    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehicle deleted.', 'success')
    return redirect(url_for('user.dashboard'))
