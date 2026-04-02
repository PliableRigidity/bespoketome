# database.py
import sqlite3
import os
from datetime import datetime
import json
import logging

DB_NAME = "vector_state.db"

# Configure Logging
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the schema."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # --- TASKS TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            status TEXT DEFAULT 'active',
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- MEMORY TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            source TEXT DEFAULT 'user',
            type TEXT DEFAULT 'pinned',
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- DOCUMENTS TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT,
            file_path TEXT,
            memory_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(memory_id) REFERENCES memories(id)
        )
    ''')

    # --- RETRIEVAL LOGS TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS retrieval_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            query TEXT,
            web_sources TEXT,  -- JSON string
            images TEXT,       -- JSON string
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            tool_name TEXT
        )
    ''')
    
    # --- RETRIEVAL SETTINGS TABLE (Single row) ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS retrieval_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            web_enabled INTEGER DEFAULT 1,
            images_enabled INTEGER DEFAULT 1,
            safe_search TEXT DEFAULT 'moderate',
            max_web_results INTEGER DEFAULT 5,
            max_image_results INTEGER DEFAULT 4
        )
    ''')
    # Insert default settings if not exists
    c.execute('INSERT OR IGNORE INTO retrieval_settings (id) VALUES (1)')

    # --- SYSTEMS LOG TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS systems_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component TEXT,
            status TEXT,
            details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- ROBOTS TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS robots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            status TEXT DEFAULT 'offline',
            capabilities TEXT, -- JSON string
            last_seen TEXT,
            notes TEXT
        )
    ''')

    # --- ROBOT COMMAND LOGS TABLE ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS robot_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id INTEGER,
            command TEXT,
            args TEXT,
            status TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(robot_id) REFERENCES robots(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

# Initialize on import
init_db()

# --- HELPER FUNCTIONS ---

def query_db(query, args=(), one=False):
    """Run a SELECT query."""
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Run an INSERT/UPDATE/DELETE query."""
    conn = get_db_connection()
    cur = conn.execute(query, args)
    conn.commit()
    last_row_id = cur.lastrowid
    conn.close()
    return last_row_id

# --- MIGRATION CHECK (Simple) ---
# Check if SimBot-01 exists, if not create it
def ensure_simbot():
    existing = query_db("SELECT * FROM robots WHERE name = ?", ("SimBot-01",), one=True)
    if not existing:
        capabilities = json.dumps(["move", "rotate", "stop", "get_state"])
        execute_db('''
            INSERT INTO robots (name, type, status, capabilities, last_seen, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("SimBot-01", "Simulated", "online", capabilities, datetime.now().isoformat(), "Default simulated robot"))

ensure_simbot()
