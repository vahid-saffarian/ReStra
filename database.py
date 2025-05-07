import sqlite3
from datetime import datetime

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('strava_bot.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            strava_access_token TEXT,
            strava_refresh_token TEXT,
            strava_token_expires_at INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(telegram_id, access_token, refresh_token, expires_at):
    """Add or update a user's Strava tokens"""
    conn = sqlite3.connect('strava_bot.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT OR REPLACE INTO users 
        (telegram_id, strava_access_token, strava_refresh_token, strava_token_expires_at)
        VALUES (?, ?, ?, ?)
    ''', (telegram_id, access_token, refresh_token, expires_at))
    
    conn.commit()
    conn.close()

def get_user(telegram_id):
    """Get user's Strava tokens"""
    conn = sqlite3.connect('strava_bot.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = c.fetchone()
    
    conn.close()
    return user

def get_all_users():
    """Get all registered users"""
    conn = sqlite3.connect('strava_bot.db')
    c = conn.cursor()
    
    c.execute('SELECT telegram_id FROM users')
    users = c.fetchall()
    
    conn.close()
    return [user[0] for user in users]

# Initialize database when module is imported
init_db() 