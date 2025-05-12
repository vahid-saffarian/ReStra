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
    """Add a user to the in-memory storage"""
    try:
        users[chat_id] = (chat_id, access_token, refresh_token, expires_at)
        logger.info(f"Added user {chat_id} to storage")
        return True
    except Exception as e:
        logger.error(f"Error adding user {chat_id}: {str(e)}")
        return False

def get_user(chat_id):
    """Get a user from the in-memory storage"""
    try:
        return users.get(chat_id)
    except Exception as e:
        logger.error(f"Error getting user {chat_id}: {str(e)}")
        return None

def remove_user(chat_id):
    """Remove a user from the in-memory storage"""
    try:
        if chat_id in users:
            del users[chat_id]
            logger.info(f"Removed user {chat_id} from storage")
            return True
        return False
    except Exception as e:
        logger.error(f"Error removing user {chat_id}: {str(e)}")
        return False

def get_all_users():
    """Get all user chat IDs"""
    try:
        return list(users.keys())
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return []

def add_auth_session(chat_id, state, timestamp):
    """Add an auth session to the in-memory storage"""
    try:
        auth_sessions[chat_id] = {
            'state': state,
            'timestamp': timestamp.isoformat()  # Convert datetime to ISO format string
        }
        logger.info(f"Added auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding auth session for {chat_id}: {str(e)}")
        return False

def get_auth_session(chat_id):
    """Get an auth session from the in-memory storage"""
    try:
        session = auth_sessions.get(chat_id)
        if session:
            # Convert ISO format string back to datetime
            session['timestamp'] = datetime.fromisoformat(session['timestamp'])
        return session
    except Exception as e:
        logger.error(f"Error getting auth session for {chat_id}: {str(e)}")
        return None

def remove_auth_session(chat_id):
    """Remove an auth session from the in-memory storage"""
    try:
        if chat_id in auth_sessions:
            del auth_sessions[chat_id]
            logger.info(f"Removed auth session for {chat_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error removing auth session for {chat_id}: {str(e)}")
        return False

def cleanup_expired_sessions():
    """Remove expired auth sessions"""
    try:
        current_time = datetime.now()
        expired_sessions = [
            chat_id for chat_id, session in auth_sessions.items()
            if (current_time - datetime.fromisoformat(session['timestamp'])).total_seconds() > 300  # 5 minutes
        ]
        for chat_id in expired_sessions:
            remove_auth_session(chat_id)
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {str(e)}") 