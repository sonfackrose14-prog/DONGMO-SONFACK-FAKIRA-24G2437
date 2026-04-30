from flask import Flask, render_template, request, redirect, url_for
from api.db import db
from flask_migrate import Migrate
from api.model import FlightLog
import os

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION POSTGRESQL (NEON / VERCEL) ---
# On récupère l'URL depuis les variables d'environnement de Vercel
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Neon fournit souvent une URL commençant par postgres:// 
    # mais SQLAlchemy exige postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Optionnel : Fallback sur SQLite pour le développement local uniquement
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Options pour maintenir la connexion active avec Neon
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
}

# Initialisation
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
        return f"Erreur de base de données : {str(e)}", 500

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
            return f"Erreur lors de l'enregistrement : {str(e)}", 500
    
    return render_template("index.html")

# --- CONFIGURATION VERCEL ---
app.debug = False

if __name__ == "__main__":
    # Pour le test en local, on peut créer les tables automatiquement
    with app.app_context():
        db.create_all()
    app.run(debug=True)