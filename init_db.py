"""
CPSMS – Database Initialization & Seed Data
Run this script once to populate the database with sample data.

Usage:
    python init_db.py
"""
from app import create_app
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.parking_slot import ParkingSlot
from models.reservation import Reservation
from datetime import date, time


def seed_database():
    """Create tables and insert sample data."""
    app = create_app()

    with app.app_context():
        # Drop and recreate all tables (fresh start)
        db.drop_all()
        db.create_all()
        print("[✓] Tables created successfully.")

        # ── Users ────────────────────────────────────────────────────
        admin = User(
            user_name='Admin User',
            email='admin@campus.edu',
            phone_number='9999900000',
            role='admin'
        )
        admin.set_password('admin123')

        student1 = User(
            user_name='John Doe',
            email='john@campus.edu',
            phone_number='9999911111',
            role='student'
        )
        student1.set_password('student123')

        student2 = User(
            user_name='Jane Smith',
            email='jane@campus.edu',
            phone_number='9999922222',
            role='student'
        )
        student2.set_password('student123')

        staff_member = User(
            user_name='Prof. Williams',
            email='williams@campus.edu',
            phone_number='9999933333',
            role='staff'
        )
        staff_member.set_password('staff123')

        parking_guard = User(
            user_name='Security Guard',
            email='guard@campus.edu',
            phone_number='9999944444',
            role='parking_staff'
        )
        parking_guard.set_password('staff123')

        student3 = User(
            user_name='Alex Kumar',
            email='alex@campus.edu',
            phone_number='9999955555',
            role='student'
        )
        student3.set_password('student123')

        db.session.add_all([admin, student1, student2, staff_member, parking_guard, student3])
        db.session.flush()  # Get IDs
        print(f"[✓] {6} users created.")

        # ── Vehicles ─────────────────────────────────────────────────
        v1 = Vehicle(user_id=student1.user_id, vehicle_number='KA-01-AB-1234', vehicle_type='Car')
        v2 = Vehicle(user_id=student1.user_id, vehicle_number='KA-01-CD-5678', vehicle_type='Bike')
        v3 = Vehicle(user_id=student2.user_id, vehicle_number='MH-12-XY-9999', vehicle_type='Scooter')
        v4 = Vehicle(user_id=staff_member.user_id, vehicle_number='KA-05-EF-4321', vehicle_type='Car')
        v5 = Vehicle(user_id=student3.user_id, vehicle_number='DL-08-GH-7777', vehicle_type='SUV')

        db.session.add_all([v1, v2, v3, v4, v5])
        db.session.flush()
        print(f"[✓] {5} vehicles registered.")

        # ── Parking Slots ────────────────────────────────────────────
        slot_locations = [
            'Block A - Slot 1', 'Block A - Slot 2', 'Block A - Slot 3',
            'Block A - Slot 4', 'Block A - Slot 5',
            'Block B - Slot 1', 'Block B - Slot 2', 'Block B - Slot 3',
            'Block B - Slot 4', 'Block B - Slot 5',
            'Block C - Slot 1', 'Block C - Slot 2', 'Block C - Slot 3',
            'Block C - Slot 4', 'Block C - Slot 5',
            'Block D - Slot 1', 'Block D - Slot 2', 'Block D - Slot 3',
            'Block D - Slot 4', 'Block D - Slot 5',
        ]

        slots = []
        for loc in slot_locations:
            slots.append(ParkingSlot(slot_location=loc, slot_status='Available', is_active=True))

        db.session.add_all(slots)
        db.session.flush()
        print(f"[✓] {len(slots)} parking slots created.")

        # ── Sample Reservations ──────────────────────────────────────
        # Student1 has an active reservation
        slots[0].slot_status = 'Occupied'
        r1 = Reservation(
            user_id=student1.user_id,
            vehicle_id=v1.vehicle_id,
            slot_id=slots[0].slot_id,
            reservation_date=date.today(),
            reservation_time=time(9, 30),
            is_active=True
        )

        # Staff member has an active reservation
        slots[5].slot_status = 'Occupied'
        r2 = Reservation(
            user_id=staff_member.user_id,
            vehicle_id=v4.vehicle_id,
            slot_id=slots[5].slot_id,
            reservation_date=date.today(),
            reservation_time=time(8, 0),
            is_active=True
        )

        # A past cancelled reservation for student2
        r3 = Reservation(
            user_id=student2.user_id,
            vehicle_id=v3.vehicle_id,
            slot_id=slots[2].slot_id,
            reservation_date=date(2026, 4, 5),
            reservation_time=time(14, 15),
            is_active=False
        )

        db.session.add_all([r1, r2, r3])
        db.session.commit()
        print(f"[✓] {3} sample reservations created (2 active, 1 cancelled).")

        print("\n" + "=" * 60)
        print("  Database initialized successfully!")
        print("=" * 60)
        print("\n  Login Credentials:")
        print("  ─────────────────────────────────────────")
        print("  Admin         → admin@campus.edu    / admin123")
        print("  Student (John)→ john@campus.edu     / student123")
        print("  Student (Jane)→ jane@campus.edu     / student123")
        print("  Student (Alex)→ alex@campus.edu     / student123")
        print("  Staff         → williams@campus.edu / staff123")
        print("  Parking Staff → guard@campus.edu    / staff123")
        print("  ─────────────────────────────────────────")
        print("\n  Run the app:  python app.py\n")


if __name__ == '__main__':
    seed_database()
