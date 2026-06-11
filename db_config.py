import os
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL')
DB_PATH = os.environ.get('SQLITE_DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'internship.db'))

def is_postgres():
    return bool(DATABASE_URL)

def placeholder():
    return '%s' if DATABASE_URL else '?'

def get_connection():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = False
        return conn
    else:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

def fetch_count(cursor):
    row = cursor.fetchone()
    if row is None:
        return 0
    if isinstance(row, dict):
        return row.get('count', row.get('COUNT', 0))
    return row[0]

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            age INTEGER,
            education TEXT,
            college TEXT,
            cgpa REAL,
            skills TEXT,
            interests TEXT,
            location_preference TEXT,
            location_type TEXT,
            category TEXT,
            experience TEXT,
            past_participation INTEGER DEFAULT 0,
            created_at TEXT,
            password TEXT DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            organization TEXT,
            sector TEXT,
            location TEXT,
            duration TEXT,
            stipend INTEGER,
            required_skills TEXT,
            education_requirement TEXT,
            description TEXT,
            capacity INTEGER,
            affirmative_action_required INTEGER DEFAULT 0,
            apply_url TEXT DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            student_id TEXT,
            matches TEXT,
            timestamp TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
