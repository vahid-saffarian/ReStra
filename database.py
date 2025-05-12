import os
import json
import logging
from datetime import datetime, timedelta
import redis

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Redis client
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)

# Key prefixes
USER_KEY_PREFIX = 'user:'
AUTH_SESSION_KEY_PREFIX = 'auth_session:'

def add_user(chat_id, access_token, refresh_token, expires_at):
    """Add a user to Redis"""
    try:
        user_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at.isoformat()
        }
        redis_client.hmset(f"{USER_KEY_PREFIX}{chat_id}", user_data)
        logger.info(f"Added user {chat_id} to Redis")
        return True
    except Exception as e:
        logger.error(f"Error adding user {chat_id}: {str(e)}")
        return False

def get_user(chat_id):
    """Get a user from Redis"""
    try:
        user_data = redis_client.hgetall(f"{USER_KEY_PREFIX}{chat_id}")
        if user_data:
            return {
                'chat_id': chat_id,
                'access_token': user_data[b'access_token'].decode('utf-8'),
                'refresh_token': user_data[b'refresh_token'].decode('utf-8'),
                'expires_at': datetime.fromisoformat(user_data[b'expires_at'].decode('utf-8'))
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user {chat_id}: {str(e)}")
        return None

def remove_user(chat_id):
    """Remove a user from Redis"""
    try:
        redis_client.delete(f"{USER_KEY_PREFIX}{chat_id}")
        logger.info(f"Removed user {chat_id} from Redis")
        return True
    except Exception as e:
        logger.error(f"Error removing user {chat_id}: {str(e)}")
        return False

def get_all_users():
    """Get all user chat IDs from Redis"""
    try:
        keys = redis_client.keys(f"{USER_KEY_PREFIX}*")
        return [key.decode('utf-8').replace(USER_KEY_PREFIX, '') for key in keys]
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return []

def add_auth_session(chat_id, state, timestamp):
    """Add an auth session to Redis"""
    try:
        session_data = {
            'state': state,
            'timestamp': timestamp.isoformat()
        }
        redis_client.hmset(f"{AUTH_SESSION_KEY_PREFIX}{chat_id}", session_data)
        # Set expiration for 5 minutes
        redis_client.expire(f"{AUTH_SESSION_KEY_PREFIX}{chat_id}", 300)
        logger.info(f"Added auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding auth session for {chat_id}: {str(e)}")
        return False

def get_auth_session(chat_id):
    """Get an auth session from Redis"""
    try:
        session_data = redis_client.hgetall(f"{AUTH_SESSION_KEY_PREFIX}{chat_id}")
        if session_data:
            return {
                'state': session_data[b'state'].decode('utf-8'),
                'timestamp': datetime.fromisoformat(session_data[b'timestamp'].decode('utf-8'))
            }
        return None
    except Exception as e:
        logger.error(f"Error getting auth session for {chat_id}: {str(e)}")
        return None

def remove_auth_session(chat_id):
    """Remove an auth session from Redis"""
    try:
        redis_client.delete(f"{AUTH_SESSION_KEY_PREFIX}{chat_id}")
        logger.info(f"Removed auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error removing auth session for {chat_id}: {str(e)}")
        return False

def cleanup_expired_sessions():
    """Cleanup is handled automatically by Redis TTL"""
    pass 