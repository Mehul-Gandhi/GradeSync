# scripts/init_database.py

import psycopg2
from src.database import connect_db

def initialize_db():
    conn = connect_db()
    if conn is None:
        print("Failed to connect to the database.")
        return

    try:
        with conn.cursor() as cursor:
            with open("db/init_db.sql", "r") as sql_file:
                cursor.execute(sql_file.read())
            conn.commit()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_db()