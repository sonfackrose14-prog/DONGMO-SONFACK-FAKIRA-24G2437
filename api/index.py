from flask import Flask, render_template, request, redirect, url_for
from api.db import db
from flask_migrate import Migrate, upgrade  # Import de 'upgrade' ajouté
from api.model import FlightLog
import os

app = Flask(__name__, template_folder='../templates')

# --- CONFIGURATION DYNAMIQUE POSTGRES ---
# On récupère l'URL de Neon (DATABASE_URL ou POSTGRES_URL)
database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

if not database_url:
    raise RuntimeError("ERREUR : Aucune variable DATABASE_URL trouvée sur Vercel.")

# Correction du protocole pour SQLAlchemy (postgres -> postgresql)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Options pour stabiliser la connexion avec Neon
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
}

# Initialisation
db.init_app(app)
migrate = Migrate(app, db)

# --- INITIALISATION AUTOMATIQUE DES TABLES ---
# Cette partie remplace le besoin de faire 'flask db upgrade' manuellement
with app.app_context():
    try:
        upgrade() 
        print("Base de données mise à jour (Migrations appliquées).")
    except Exception as e:
        print(f"Note : Initialisation via upgrade a échoué (souvent normal si déjà fait) : {e}")

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
            # Création de l'entrée pour l'application d'aviation
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

# Configuration pour Vercel
app.debug = False

if __name__ == "__main__":
    app.run(debug=True)