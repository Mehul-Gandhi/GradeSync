# src/database.py

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv(dotenv_path='../db/config.env')

def connect_db():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None