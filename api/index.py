from flask import Flask, render_template, request, redirect, url_for
from api.db import db
from flask_migrate import Migrate
from api.model import FlightLog
import os

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION DYNAMIQUE ---
# On essaie de récupérer l'URL, peu importe le nom donné par Vercel/Neon
database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

if not database_url:
    raise RuntimeError("ERREUR : Aucune variable de base de données trouvée dans l'environnement Vercel.")

# CRUCIAL : SQLAlchemy exige 'postgresql://' et non 'postgres://'
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration pour éviter les déconnexions avec Neon
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db.init_app(app)
Migrate(app, db)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list')
def list_flights():
    try:
        flights = FlightLog.query.order_by(FlightLog.date_posted.desc()).all()
        return render_template("list.html", users=flights)
    except Exception as e:
        return f"Erreur de lecture : {str(e)}", 500

@app.route('/submit-flight', methods=['GET', 'POST'])
def submit_flight():
    if request.method == 'POST':
        try:
            instance = FlightLog(
                origin=request.form.get("origin"),
                destination=request.form.get("destination"),
                duration=float(request.form.get("duration")),
                aircraft_tail_number=request.form.get("aircraft_tail_number"),
                pilot_name=request.form.get("pilot_name"),
                submitted_by=request.form.get("submitted_by")
            )
            db.session.add(instance)
            db.session.commit()
            return redirect(url_for('list_flights'))
        except Exception as e:
            db.session.rollback()
            return f"Erreur d'enregistrement : {str(e)}", 500
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)