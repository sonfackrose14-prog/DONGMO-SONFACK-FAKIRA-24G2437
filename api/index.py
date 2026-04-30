from flask import Flask, render_template, request, redirect
from db import db
from flask_migrate import Migrate
from model import FlightLog

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list')
def list():
    utilisateur = FlightLog.query.all()
    return render_template("list.html", users=utilisateur)

@app.route('/submit-flight', methods=['GET', 'POST'])
def submit_flight():
    if request.method == 'POST':
        origin = request.form.get("origin")
        destination = request.form.get("destination")
        duration = request.form.get("duration")
        aircraft_tail_number = request.form.get("aircraft_tail_number")
        pilot_name = request.form.get("pilot_name")        # ✅ corrigé
        submitted_by = request.form.get("submitted_by")
        instance = FlightLog(origin, destination, duration, aircraft_tail_number, pilot_name, submitted_by)
        db.session.add(instance)
        db.session.commit()
        return redirect('/list')
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)