import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

conn = psycopg2.connect(
    dbname=os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=5432
)

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    money INTEGER
);
""")
conn.commit()
