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

# In-memory storage for users
users = {}

# File path for auth sessions
AUTH_SESSIONS_FILE = '/tmp/auth_sessions.json'

def _load_auth_sessions():
    """Load auth sessions from file"""
    try:
        if os.path.exists(AUTH_SESSIONS_FILE):
            with open(AUTH_SESSIONS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading auth sessions: {str(e)}")
        return {}

def _save_auth_sessions(sessions):
    """Save auth sessions to file"""
    try:
        with open(AUTH_SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f)
    except Exception as e:
        logger.error(f"Error saving auth sessions: {str(e)}")

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
    """Add an auth session to storage"""
    try:
        sessions = _load_auth_sessions()
        sessions[str(chat_id)] = {
            'state': state,
            'timestamp': timestamp.isoformat()
        }
        _save_auth_sessions(sessions)
        logger.info(f"Added auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding auth session for {chat_id}: {str(e)}")
        return False

def get_auth_session(chat_id):
    """Get an auth session from storage"""
    try:
        sessions = _load_auth_sessions()
        session = sessions.get(str(chat_id))
        if session:
            # Convert ISO format string back to datetime
            session['timestamp'] = datetime.fromisoformat(session['timestamp'])
        return session
    except Exception as e:
        logger.error(f"Error getting auth session for {chat_id}: {str(e)}")
        return None

def remove_auth_session(chat_id):
    """Remove an auth session from storage"""
    try:
        sessions = _load_auth_sessions()
        if str(chat_id) in sessions:
            del sessions[str(chat_id)]
            _save_auth_sessions(sessions)
            logger.info(f"Removed auth session for {chat_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error removing auth session for {chat_id}: {str(e)}")
        return False

def cleanup_expired_sessions():
    """Remove expired auth sessions"""
    try:
        sessions = _load_auth_sessions()
        current_time = datetime.now()
        expired_sessions = [
            chat_id for chat_id, session in sessions.items()
            if (current_time - datetime.fromisoformat(session['timestamp'])).total_seconds() > 300  # 5 minutes
        ]
        for chat_id in expired_sessions:
            del sessions[chat_id]
        _save_auth_sessions(sessions)
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {str(e)}") 