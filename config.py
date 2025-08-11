import urllib.parse
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# Create database if it doesn't exist
def setup_database():
    """
    Determine SQLAlchemy database URI.
    - Production: Use DATABASE_URL if provided (e.g., PlanetScale, RDS, etc.)
    - Otherwise: Build from individual env vars or fall back to a local MySQL instance.
      In local dev only, attempt to create the DB if host is localhost.
    """
    # 1) Prefer a full DATABASE_URL if present
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Support users pasting the full `psql 'postgresql://...'` command
        try:
            url = database_url.strip()
            # If value looks like: psql 'postgresql://...'
            if url.lower().startswith('psql '):
                import shlex
                parts = shlex.split(url)
                if len(parts) >= 2:
                    url = parts[1]
            # Strip surrounding quotes if present
            url = url.strip('"\'')
            # Normalize scheme for SQLAlchemy/psycopg2
            if url.startswith('postgres://'):
                url = url.replace('postgres://', 'postgresql+psycopg2://', 1)
            elif url.startswith('postgresql://'):
                url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
            return url
        except Exception as e:
            print(f"[setup_database] Failed to normalize DATABASE_URL, using raw value: {e}")
            return database_url

    # 2) Compose from individual parts (env-overridable)
    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'root')
    raw_password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'ecofinds')

    password = urllib.parse.quote_plus(raw_password)

    # 3) In local environments, try to create the database if it doesn't exist
    if host in ('localhost', '127.0.0.1'):
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=raw_password
            )
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            connection.close()
        except Exception as e:
            print(f"[setup_database] Skipping DB auto-create (non-fatal): {e}")

    # 4) Return SQLAlchemy URI (works for both local and hosted MySQL)
    return f'mysql+pymysql://{user}:{password}@{host}/{db_name}'
