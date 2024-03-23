from app import app, db  # Import the Flask app instance and the SQLAlchemy instance

# Create the database tables
with app.app_context():
    db.create_all()

