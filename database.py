from flask_sqlalchemy import SQLAlchemy


try:
    db = SQLAlchemy()
    print("Connected to DB")
except Exception as e:
    print(f"Failed to initialize database: {e}")
