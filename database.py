import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Use in-memory database for serverless environment
conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id TEXT PRIMARY KEY,
    access_token TEXT,
    refresh_token TEXT,
    expires_at INTEGER
)
''')
conn.commit()

def add_user(chat_id, access_token, refresh_token, expires_at):
    """Add or update a user in the database"""
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO users (chat_id, access_token, refresh_token, expires_at)
        VALUES (?, ?, ?, ?)
        ''', (chat_id, access_token, refresh_token, expires_at))
        conn.commit()
        logger.info(f"User {chat_id} added/updated in database")
    except Exception as e:
        logger.error(f"Error adding user to database: {str(e)}")

def get_user(chat_id):
    """Get a user from the database"""
    try:
        cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error getting user from database: {str(e)}")
        return None

def get_all_users():
    """Get all users from the database"""
    try:
        cursor.execute('SELECT chat_id FROM users')
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error getting all users from database: {str(e)}")
        return [] 