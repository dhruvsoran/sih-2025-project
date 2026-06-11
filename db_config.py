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
    if hasattr(row, 'keys'):
        for key in row.keys():
            return row[key]
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

    # Run migrations for existing databases
    _migrate()


def _migrate():
    """Add columns to existing tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if is_postgres():
            # PostgreSQL: check if column exists then add
            cursor.execute("""
                DO $$ BEGIN
                    ALTER TABLE students ADD COLUMN IF NOT EXISTS email_verified INTEGER DEFAULT 0;
                EXCEPTION WHEN duplicate_column THEN NULL;
                END $$;
            """)
            cursor.execute("""
                DO $$ BEGIN
                    ALTER TABLE students ADD COLUMN IF NOT EXISTS verification_token TEXT DEFAULT '';
                EXCEPTION WHEN duplicate_column THEN NULL;
                END $$;
            """)
        else:
            # SQLite: check and add columns
            cursor.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'email_verified' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN email_verified INTEGER DEFAULT 0")
            if 'verification_token' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN verification_token TEXT DEFAULT ''")
        conn.commit()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Migration note: {e}")
    finally:
        cursor.close()
        conn.close()
