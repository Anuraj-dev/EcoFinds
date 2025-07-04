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
    password = urllib.parse.quote_plus('Raja@784175')
    
    # First connect to MySQL without specifying a database to create the database if it doesn't exist
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Raja@784175'
        )
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS ecofinds")
        connection.close()
    except Exception as e:
        print(f"Error creating database: {e}")
    
    # Return database URI
    return f'mysql+pymysql://root:{password}@localhost/ecofinds'
