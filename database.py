import os
import json
import logging
from datetime import datetime
from vercel_kv import kv

logger = logging.getLogger(__name__)

def add_user(chat_id, access_token, refresh_token, expires_at):
    """Add or update a user in the database"""
    try:
        user_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
        kv.set(f"user:{chat_id}", json.dumps(user_data))
        logger.info(f"User {chat_id} added/updated in database")
    except Exception as e:
        logger.error(f"Error adding user to database: {str(e)}")

def get_user(chat_id):
    """Get a user from the database"""
    try:
        user_data = kv.get(f"user:{chat_id}")
        if user_data:
            data = json.loads(user_data)
            return (chat_id, data['access_token'], data['refresh_token'], data['expires_at'])
        return None
    except Exception as e:
        logger.error(f"Error getting user from database: {str(e)}")
        return None

def get_all_users():
    """Get all users from the database"""
    try:
        # Get all keys that start with "user:"
        keys = kv.keys("user:*")
        return [key.split(":")[1] for key in keys]
    except Exception as e:
        logger.error(f"Error getting all users from database: {str(e)}")
        return []

def add_auth_session(chat_id, state, timestamp):
    """Add an auth session to the database"""
    try:
        session_data = {
            'state': state,
            'timestamp': timestamp.isoformat()
        }
        kv.set(f"auth_session:{chat_id}", json.dumps(session_data))
        logger.info(f"Auth session added for chat_id {chat_id}")
    except Exception as e:
        logger.error(f"Error adding auth session: {str(e)}")

def get_auth_session(chat_id):
    """Get an auth session from the database"""
    try:
        session_data = kv.get(f"auth_session:{chat_id}")
        if session_data:
            data = json.loads(session_data)
            return {
                'state': data['state'],
                'timestamp': datetime.fromisoformat(data['timestamp'])
            }
        return None
    except Exception as e:
        logger.error(f"Error getting auth session: {str(e)}")
        return None

def remove_auth_session(chat_id):
    """Remove an auth session from the database"""
    try:
        kv.delete(f"auth_session:{chat_id}")
        logger.info(f"Auth session removed for chat_id {chat_id}")
    except Exception as e:
        logger.error(f"Error removing auth session: {str(e)}")

def cleanup_expired_sessions():
    """Remove expired auth sessions"""
    try:
        keys = kv.keys("auth_session:*")
        current_time = datetime.now()
        for key in keys:
            session_data = kv.get(key)
            if session_data:
                data = json.loads(session_data)
                session_time = datetime.fromisoformat(data['timestamp'])
                if (current_time - session_time).total_seconds() > 300:  # 5 minutes
                    kv.delete(key)
                    logger.info(f"Expired auth session removed: {key}")
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {str(e)}") 