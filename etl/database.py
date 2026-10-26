import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connect(dbname=None):
    """Connect to PostgreSQL using the settings in .env."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=dbname or os.getenv("DB_NAME", "chelsea"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )
