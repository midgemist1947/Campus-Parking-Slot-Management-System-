from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.vehicle import Vehicle
from models.parking_slot import ParkingSlot
from models.reservation import Reservation
from models.report import Report
