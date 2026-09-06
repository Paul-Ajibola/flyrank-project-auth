import os
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Create the tasks table if it does not exist on startup."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
            );
            """)
            conn.commit()

def insert_sample_tasks():
    """Insert sample tasks if the table is empty."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tasks")
            count = cur.fetchone()["count"]
            
            if count == 0:
                sample_tasks = [
                    ("remove trash", False),
                    ("wash cloth", False),
                    ("polish shoes", False),
                ]
                cur.executemany("INSERT INTO tasks (title, done) VALUES (%s, %s)", sample_tasks)
                conn.commit()
                print("Inserted sample tasks")