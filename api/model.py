from datetime import datetime
from db import db

class FlightLog(db.Model):
    __tablename__ = 'flight_logs'

    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    origin = db.Column(db.String(10))
    destination = db.Column(db.String(10))
    duration = db.Column(db.Float)
    aircraft_tail_number = db.Column(db.String(20))
    pilot_name = db.Column(db.String(100))
    submitted_by = db.Column(db.String(100))

    def __init__(self, origin, destination, duration, aircraft_tail_number, pilot_name, submitted_by, date_posted=None):
        self.origin = origin
        self.destination = destination
        self.duration = duration
        self.aircraft_tail_number = aircraft_tail_number
        self.pilot_name = pilot_name
        self.submitted_by = submitted_by
        if date_posted:
            self.date_posted = date_posted