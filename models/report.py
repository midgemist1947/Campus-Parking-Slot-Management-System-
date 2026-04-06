from models import db
from datetime import date


class Report(db.Model):
    """Admin-generated report metadata."""
    __tablename__ = 'reports'

    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    report_type = db.Column(db.String(50), nullable=False)  # bookings / peak_hours / utilization

    def __repr__(self):
        return f'<Report {self.report_id} type={self.report_type}>'
