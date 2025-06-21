import urllib.parse
import pymysql

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
        print("Database 'ecofinds' checked/created successfully")
    except Exception as e:
        print(f"Error creating database: {e}")
    
    # Return database URI
    return f'mysql+pymysql://root:{password}@localhost/ecofinds'
