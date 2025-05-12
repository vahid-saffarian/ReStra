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
logger.info(f"Initializing Redis client with URL: {redis_url}")
redis_client = redis.from_url(redis_url)

# Test Redis connection
try:
    redis_client.ping()
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {str(e)}")

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
        key = f"{USER_KEY_PREFIX}{chat_id}"
        logger.info(f"Adding user data to Redis with key: {key}")
        redis_client.hmset(key, user_data)
        logger.info(f"Successfully added user {chat_id} to Redis")
        return True
    except Exception as e:
        logger.error(f"Error adding user {chat_id}: {str(e)}")
        return False

def get_user(chat_id):
    """Get a user from Redis"""
    try:
        key = f"{USER_KEY_PREFIX}{chat_id}"
        logger.info(f"Getting user data from Redis with key: {key}")
        user_data = redis_client.hgetall(key)
        if user_data:
            logger.info(f"Found user data for {chat_id}")
            return {
                'chat_id': chat_id,
                'access_token': user_data[b'access_token'].decode('utf-8'),
                'refresh_token': user_data[b'refresh_token'].decode('utf-8'),
                'expires_at': datetime.fromisoformat(user_data[b'expires_at'].decode('utf-8'))
            }
        logger.info(f"No user data found for {chat_id}")
        return None
    except Exception as e:
        logger.error(f"Error getting user {chat_id}: {str(e)}")
        return None

def remove_user(chat_id):
    """Remove a user from Redis"""
    try:
        key = f"{USER_KEY_PREFIX}{chat_id}"
        logger.info(f"Removing user data from Redis with key: {key}")
        redis_client.delete(key)
        logger.info(f"Successfully removed user {chat_id} from Redis")
        return True
    except Exception as e:
        logger.error(f"Error removing user {chat_id}: {str(e)}")
        return False

def get_all_users():
    """Get all user chat IDs from Redis"""
    try:
        pattern = f"{USER_KEY_PREFIX}*"
        logger.info(f"Getting all users from Redis with pattern: {pattern}")
        keys = redis_client.keys(pattern)
        users = [key.decode('utf-8').replace(USER_KEY_PREFIX, '') for key in keys]
        logger.info(f"Found {len(users)} users in Redis")
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return []

def add_auth_session(chat_id, state, timestamp):
    """Add an auth session to Redis"""
    try:
        key = f"{AUTH_SESSION_KEY_PREFIX}{chat_id}"
        logger.info(f"Adding auth session to Redis with key: {key}")
        session_data = {
            'state': state,
            'timestamp': timestamp.isoformat()
        }
        redis_client.hmset(key, session_data)
        # Set expiration for 5 minutes
        redis_client.expire(key, 300)
        logger.info(f"Successfully added auth session for {chat_id} with state {state}")
        return True
    except Exception as e:
        logger.error(f"Error adding auth session for {chat_id}: {str(e)}")
        return False

def get_auth_session(chat_id):
    """Get an auth session from Redis"""
    try:
        key = f"{AUTH_SESSION_KEY_PREFIX}{chat_id}"
        logger.info(f"Getting auth session from Redis with key: {key}")
        session_data = redis_client.hgetall(key)
        if session_data:
            logger.info(f"Found auth session for {chat_id}")
            return {
                'state': session_data[b'state'].decode('utf-8'),
                'timestamp': datetime.fromisoformat(session_data[b'timestamp'].decode('utf-8'))
            }
        logger.info(f"No auth session found for {chat_id}")
        return None
    except Exception as e:
        logger.error(f"Error getting auth session for {chat_id}: {str(e)}")
        return None

def remove_auth_session(chat_id):
    """Remove an auth session from Redis"""
    try:
        key = f"{AUTH_SESSION_KEY_PREFIX}{chat_id}"
        logger.info(f"Removing auth session from Redis with key: {key}")
        redis_client.delete(key)
        logger.info(f"Successfully removed auth session for {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error removing auth session for {chat_id}: {str(e)}")
        return False

def cleanup_expired_sessions():
    """Cleanup is handled automatically by Redis TTL"""
    pass 