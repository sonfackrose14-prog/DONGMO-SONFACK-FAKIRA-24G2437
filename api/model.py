from datetime import datetime
from api.db import db

class FlightLog(db.Model):
    __tablename__ = 'flight_logs'

    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    origin = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(10), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    aircraft_tail_number = db.Column(db.String(20), nullable=False)
    pilot_name = db.Column(db.String(100), nullable=False)
    submitted_by = db.Column(db.String(100), nullable=False)

    def __init__(self, origin, destination, duration, aircraft_tail_number, pilot_name, submitted_by, date_posted=None):
        self.origin = origin
        self.destination = destination
        self.duration = duration
        self.aircraft_tail_number = aircraft_tail_number
        self.pilot_name = pilot_name
        self.submitted_by = submitted_by
        if date_posted:
            self.date_posted = date_posted

    def to_dict(self):
        return {
            'id': self.id,
            'origin': self.origin,
            'destination': self.destination,
            'duration': self.duration,
            'aircraft_tail_number': self.aircraft_tail_number,
            'pilot_name': self.pilot_name,
            'submitted_by': self.submitted_by,
            'date_posted': self.date_posted.isoformat() if self.date_posted else None
        }