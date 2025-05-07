import os
import json
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage
users = {}
auth_sessions = {}

def add_user(chat_id, access_token, refresh_token, expires_at):
    """Add or update a user in the database"""
    try:
        users[str(chat_id)] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
        logger.info(f"Added/updated user {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding user {chat_id}: {str(e)}")
        return False

def get_user(chat_id):
    """Get a user from the database"""
    try:
        return users.get(str(chat_id))
    except Exception as e:
        logger.error(f"Error getting user {chat_id}: {str(e)}")
        return None

def get_all_users():
    """Get all users from the database"""
    try:
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return {}

def add_auth_session(chat_id, state, timestamp):
    """Add an auth session to the database"""
    try:
        auth_sessions[str(chat_id)] = {
            'state': state,
            'timestamp': timestamp
        }
        logger.info(f"Added auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding auth session for {chat_id}: {str(e)}")
        return False

def get_auth_session(chat_id):
    """Get an auth session from the database"""
    try:
        session = auth_sessions.get(str(chat_id))
        if session:
            # Convert timestamp string back to datetime
            session['timestamp'] = datetime.fromisoformat(session['timestamp'])
        return session
    except Exception as e:
        logger.error(f"Error getting auth session for {chat_id}: {str(e)}")
        return None

def remove_auth_session(chat_id):
    """Remove an auth session from the database"""
    try:
        if str(chat_id) in auth_sessions:
            del auth_sessions[str(chat_id)]
            logger.info(f"Removed auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error removing auth session for {chat_id}: {str(e)}")
        return False

def cleanup_expired_sessions():
    """Remove expired auth sessions"""
    try:
        now = datetime.now()
        expired = [
            chat_id for chat_id, session in auth_sessions.items()
            if now - session['timestamp'] > timedelta(minutes=5)
        ]
        for chat_id in expired:
            del auth_sessions[chat_id]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {str(e)}") 