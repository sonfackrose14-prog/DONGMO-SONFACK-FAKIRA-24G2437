from flask import Flask, render_template, request, redirect, url_for
from api.db import db
from flask_migrate import Migrate
from api.model import FlightLog
import os

app = Flask(__name__, template_folder='../templates')

# Configuration PostgreSQL pour Neon
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://username:password@hostname/database'
).replace('postgres://', 'postgresql://')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db.init_app(app)
Migrate(app, db)

# Création des tables au démarrage
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list')
def list_flights():
    flights = FlightLog.query.order_by(FlightLog.date_posted.desc()).all()
    return render_template("list.html", users=flights)

@app.route('/submit-flight', methods=['GET', 'POST'])
def submit_flight():
    if request.method == 'POST':
        try:
            origin = request.form.get("origin")
            destination = request.form.get("destination")
            duration = float(request.form.get("duration"))
            aircraft_tail_number = request.form.get("aircraft_tail_number")
            pilot_name = request.form.get("pilot_name")
            submitted_by = request.form.get("submitted_by")
            
            instance = FlightLog(
                origin=origin,
                destination=destination,
                duration=duration,
                aircraft_tail_number=aircraft_tail_number,
                pilot_name=pilot_name,
                submitted_by=submitted_by
            )
            db.session.add(instance)
            db.session.commit()
            return redirect(url_for('list_flights'))
        except Exception as e:
            db.session.rollback()
            return f"Erreur: {str(e)}", 500
    
    return render_template("index.html")

# Pour Vercel (obligatoire)
app.debug = False

# Pour test local
if __name__ == "__main__":
    app.run(debug=True)