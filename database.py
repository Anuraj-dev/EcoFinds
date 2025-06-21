from flask_sqlalchemy import SQLAlchemy

# Initialize the database object to be used by the app and models
try:
    db = SQLAlchemy()
    print("Connected to DB")
except Exception as e:
    print(f"Failed to initialize database: {e}")
