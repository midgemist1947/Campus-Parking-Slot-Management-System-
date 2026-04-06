from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify, Response
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.parking_slot import ParkingSlot
from models.reservation import Reservation
from models.report import Report
from utils.decorators import admin_required
from datetime import datetime, date
from sqlalchemy import func
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with analytics overview."""
    total_users = User.query.count()
    total_slots = ParkingSlot.query.filter_by(is_active=True).count()
    available_slots = ParkingSlot.query.filter_by(is_active=True, slot_status='Available').count()
    occupied_slots = ParkingSlot.query.filter_by(is_active=True, slot_status='Occupied').count()
    total_reservations = Reservation.query.count()
    active_reservations = Reservation.query.filter_by(is_active=True).count()

    users = User.query.order_by(User.user_id).all()
    slots = ParkingSlot.query.order_by(ParkingSlot.slot_id).all()
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(50).all()

    return render_template('dashboard/admin.html',
                           total_users=total_users,
                           total_slots=total_slots,
                           available_slots=available_slots,
                           occupied_slots=occupied_slots,
                           total_reservations=total_reservations,
                           active_reservations=active_reservations,
                           users=users,
                           slots=slots,
                           reservations=reservations)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLOT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/slot/add', methods=['POST'])
@admin_required
def add_slot():
    location = request.form.get('slot_location', '').strip()
    if not location:
        flash('Slot location is required.', 'danger')
        return redirect(url_for('admin.dashboard'))

    slot = ParkingSlot(slot_location=location, slot_status='Available', is_active=True)
    db.session.add(slot)
    db.session.commit()
    flash(f'Slot at "{location}" created.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/slot/edit/<int:slot_id>', methods=['POST'])
@admin_required
def edit_slot(slot_id):
    slot = ParkingSlot.query.get_or_404(slot_id)
    location = request.form.get('slot_location', '').strip()
    if location:
        slot.slot_location = location
    db.session.commit()
    flash('Slot updated.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/slot/delete/<int:slot_id>', methods=['POST'])
@admin_required
def delete_slot(slot_id):
    """Soft-delete: set is_active = False instead of removing from DB."""
    slot = ParkingSlot.query.get_or_404(slot_id)
    # If slot has an active reservation, cancel it first
    active_res = Reservation.query.filter_by(slot_id=slot_id, is_active=True).first()
    if active_res:
        active_res.is_active = False
    slot.is_active = False
    slot.slot_status = 'Available'
    db.session.commit()
    flash('Slot deactivated.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/slot/restore/<int:slot_id>', methods=['POST'])
@admin_required
def restore_slot(slot_id):
    """Restore a soft-deleted slot."""
    slot = ParkingSlot.query.get_or_404(slot_id)
    slot.is_active = True
    db.session.commit()
    flash('Slot restored.', 'success')
    return redirect(url_for('admin.dashboard'))


# ═══════════════════════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/user/add', methods=['POST'])
@admin_required
def add_user():
    name = request.form.get('user_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone_number', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'student')

    if not name or not email or not password:
        flash('Name, email, and password are required.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'warning')
        return redirect(url_for('admin.dashboard'))

    user = User(user_name=name, email=email, phone_number=phone, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'User "{name}" created.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/deactivate/<int:user_id>', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id == session['user_id']:
        flash('You cannot deactivate yourself.', 'warning')
        return redirect(url_for('admin.dashboard'))
    user.is_locked = True
    db.session.commit()
    flash(f'User "{user.user_name}" deactivated.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/activate/<int:user_id>', methods=['POST'])
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_locked = False
    user.login_attempts = 0
    db.session.commit()
    flash(f'User "{user.user_name}" activated and login attempts reset.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/reset-password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '')
    if not new_password:
        flash('New password is required.', 'danger')
        return redirect(url_for('admin.dashboard'))
    user.set_password(new_password)
    user.login_attempts = 0
    user.is_locked = False
    db.session.commit()
    flash(f'Password for "{user.user_name}" has been reset.', 'success')
    return redirect(url_for('admin.dashboard'))


# ═══════════════════════════════════════════════════════════════════════════════
#  REPORTS & ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/api/reports/summary')
@admin_required
def report_summary():
    """JSON summary for analytics dashboard."""
    total_bookings = Reservation.query.count()
    active_bookings = Reservation.query.filter_by(is_active=True).count()
    cancelled_bookings = total_bookings - active_bookings

    # Peak hours – count reservations by hour
    hour_counts = db.session.query(
        func.extract('hour', Reservation.reservation_time).label('hour'),
        func.count().label('cnt')
    ).group_by('hour').order_by('hour').all()

    peak_hours = [{'hour': int(h), 'count': c} for h, c in hour_counts]

    # Slot utilization
    total_slots = ParkingSlot.query.filter_by(is_active=True).count()
    occupied = ParkingSlot.query.filter_by(is_active=True, slot_status='Occupied').count()
    utilization = round((occupied / total_slots * 100), 1) if total_slots else 0

    return jsonify({
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings,
        'peak_hours': peak_hours,
        'utilization_percent': utilization,
        'total_slots': total_slots,
        'occupied_slots': occupied,
    })


@admin_bp.route('/reports/export-csv')
@admin_required
def export_csv():
    """Export all reservations as CSV."""
    reservations = db.session.query(
        Reservation, User, Vehicle, ParkingSlot
    ).join(User, Reservation.user_id == User.user_id
    ).join(Vehicle, Reservation.vehicle_id == Vehicle.vehicle_id
    ).join(ParkingSlot, Reservation.slot_id == ParkingSlot.slot_id
    ).order_by(Reservation.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Reservation ID', 'User', 'Email', 'Vehicle', 'Vehicle Type',
                     'Slot Location', 'Date', 'Time', 'Active'])
    for r, u, v, s in reservations:
        writer.writerow([r.reservation_id, u.user_name, u.email, v.vehicle_number,
                         v.vehicle_type, s.slot_location,
                         r.reservation_date.isoformat(), str(r.reservation_time),
                         'Yes' if r.is_active else 'No'])

    # Log report generation
    report = Report(admin_id=session['user_id'], report_type='csv_export')
    db.session.add(report)
    db.session.commit()

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=reservations_{date.today().isoformat()}.csv'}
    )
