"""
SQLite connection manager for the Cohort Refinement Assistant.
"""
import os
import sqlite3
from config import Config


def get_db_path():
    """Return the absolute path to the SQLite database."""
    return os.path.abspath(Config.SQLITE_DB_PATH)


def get_connection():
    """Create and return a new SQLite connection."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def query_db(query, args=(), one=False):
    """Execute a query and return results as list of dicts."""
    conn = get_connection()
    try:
        cur = conn.execute(query, args)
        rows = cur.fetchall()
        return (dict(rows[0]) if rows else None) if one else [dict(r) for r in rows]
    finally:
        conn.close()


def execute_db(query, args=()):
    """Execute a write query."""
    conn = get_connection()
    try:
        conn.execute(query, args)
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    from database.models import CREATE_TABLES_SQL

    conn = get_connection()
    try:
        for sql in CREATE_TABLES_SQL:
            conn.execute(sql)
        conn.commit()
    finally:
        conn.close()
