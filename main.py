import os
import requests
import time
import logging
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from strava_auth import get_strava_header, get_strava_auth_url, exchange_code_for_token
import database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only use stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REDIRECT_URI = os.getenv('STRAVA_REDIRECT_URI')

# Log loaded environment variables (excluding secrets)
logger.info(f"Loaded environment variables - Client ID: {STRAVA_CLIENT_ID}, Redirect URI: {STRAVA_REDIRECT_URI}")

# Global variables
auth_sessions = {}

# List of inspirational messages
INSPIRATIONAL_MESSAGES = [
    "😏 Netflix can wait, your future self can't!",
    "💪 Time to make your couch jealous!",
    "🌟 Your future self is judging your current self's choices...",
    "🎯 Every step counts... unless you're running in place!",
    "🔥 Ready to turn 'I'll do it tomorrow' into 'I did it yesterday'?",
    "🏃‍♂️ The only bad workout is the one you're not doing!",
    "💫 Your potential is limitless... unlike your excuses!",
    "🌈 Make today's workout count... or don't, I'm not your mom!",
    "🚀 Small steps lead to big changes... and big muscles!",
    "💪 No pain, no gain... but the gain is worth the pain!",
    "🌟 You're stronger than you think... and definitely stronger than your excuses!",
    "🎯 Time to level up your fitness game... your character needs XP!",
    "🔥 Let's turn 'I can't' into 'I did'... and 'I won't' into 'I did it twice'!",
    "🏃‍♂️ Your next PR is waiting for you... and it's getting impatient!",
    "💫 The only way to do it is to do it... unless you've found a way to teleport to the finish line!"
]

# List of greetings
GREETINGS = [
    "Hey there! 👋",
    "Hello! 🌟",
    "Hi! ✨",
    "Greetings! 🌈",
    "Hey! 🦄",
    "Hello there! 🌞",
    "Hi there! 🌺",
    "Hey hey! 🎉",
    "Hello friend! 🌻",
    "Hi buddy! 🌸",
    "Hey champ! 🏆",
    "Hello superstar! ⭐",
    "Hi legend! 🌟",
    "Hey warrior! 💪",
    "Hello champion! 🏅"
]

# List of cheering phrases
CHEERING_PHRASES = [
    'Kudos to "{name}"!',
    'Way to go, "{name}"!',
    'Amazing work, "{name}"!',
    'Incredible effort, "{name}"!',
    'Fantastic job, "{name}"!',
    'Outstanding work, "{name}"!',
    'Brilliant performance, "{name}"!',
    'Excellent work, "{name}"!',
    'Superb effort, "{name}"!',
    'Tremendous job, "{name}"!',
    'Outstanding achievement, "{name}"!',
    'Remarkable work, "{name}"!',
    'Impressive performance, "{name}"!',
    'Stellar effort, "{name}"!',
    'Magnificent work, "{name}"!'
]

# List of sign-off messages
SIGNOFF_MESSAGES = [
    "See you l8r 🐊",
    "Keep crushing it! 💪",
    "Until next time! 🚀",
    "Stay awesome! 🌟",
    "Keep moving! 🏃‍♂️",
    "You're doing great! 🎯",
    "Stay motivated! 💫",
    "Keep pushing! 🔥",
    "Stay strong! 💪",
    "Keep shining! ✨",
    "Stay legendary! 🏆",
    "Keep inspiring! 🌈",
    "Stay unstoppable! 🚀",
    "Keep being amazing! 🌟",
    "Stay awesome! 🎯"
]

def get_random_inspiration():
    """Get a random inspirational message"""
    return random.choice(INSPIRATIONAL_MESSAGES)

def get_random_greeting():
    """Get a random greeting"""
    return random.choice(GREETINGS)

def get_random_cheer():
    """Get a random cheering phrase"""
    return random.choice(CHEERING_PHRASES)

def get_random_signoff():
    """Get a random sign-off message"""
    return random.choice(SIGNOFF_MESSAGES)

def handle_start(chat_id):
    """Handle /start command"""
    message = """
Welcome to the Strava Kudos Bot! 🏃‍♂️

To get started:
1. Use /connect to link your Strava account
2. Once connected, you'll receive kudos for your activities automatically!

Use /help to see all available commands.
"""
    send_telegram_message(message, chat_id)

def handle_help(chat_id):
    """Handle /help command"""
    message = """
Available commands:
/start - Start the bot
/connect - Connect your Strava account
/disconnect - Disconnect your Strava account
/status - Check your connection status
/help - Show this help message
"""
    send_telegram_message(message, chat_id)

def handle_connect(chat_id):
    """Handle /connect command"""
    # Check if user already has an active session
    session = database.get_auth_session(chat_id)
    if session:
        message = "You already have an active connection session. Please complete the current authorization process or wait for it to expire."
        send_telegram_message(message, chat_id)
        return
    
    # Check if bot is properly configured
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        message = "❌ Error: Bot is not properly configured. Please contact the bot administrator."
        send_telegram_message(message, chat_id)
        return
        
    # Generate authorization URL using the function from strava_auth.py
    auth_url = get_strava_auth_url()
    if not auth_url:
        message = "❌ Error: Could not generate authorization URL. Please try again later."
        send_telegram_message(message, chat_id)
        return
    
    # Create new auth session
    state = random.randint(100000, 999999)
    timestamp = datetime.now()
    database.add_auth_session(chat_id, state, timestamp)
    
    message = f"""
To connect your Strava account:

1. Click this link: {auth_url}
2. Log in to your Strava account
3. Authorize the bot to access your activities
4. You'll be redirected to a page with your authorization code
5. Copy the code and send it back to me

You have 5 minutes to complete this process.
"""
    send_telegram_message(message, chat_id)

def handle_disconnect(chat_id):
    """Handle /disconnect command"""
    try:
        user = database.get_user(chat_id)
        if user:
            database.add_user(chat_id, None, None, None)
            message = "Your Strava account has been disconnected. Use /connect to link a new account."
        else:
            message = "You don't have a connected Strava account."
        send_telegram_message(message, chat_id)
    except Exception as e:
        logger.error(f"Error in handle_disconnect: {str(e)}")
        message = "❌ An error occurred while disconnecting your account. Please try again."
        send_telegram_message(message, chat_id)

def handle_status(chat_id):
    """Handle /status command"""
    try:
        user = database.get_user(chat_id)
        if user and user[1]:  # Check if user has access token
            message = "✅ Your Strava account is connected!"
        else:
            message = "❌ Your Strava account is not connected. Use /connect to link your account."
        send_telegram_message(message, chat_id)
    except Exception as e:
        logger.error(f"Error in handle_status: {str(e)}")
        message = "❌ An error occurred while checking your status. Please try again."
        send_telegram_message(message, chat_id)

def handle_auth_code(chat_id, code):
    """Handle Strava authorization code"""
    try:
        logger.info(f"Received authorization code for chat_id {chat_id}")
        
        # Check if the session exists
        session = database.get_auth_session(chat_id)
        if not session:
            logger.error(f"No active session found for chat_id {chat_id}")
            message = "❌ Your authorization session has expired. Please use /connect to start again."
            send_telegram_message(message, chat_id)
            return
            
        # Check if the session has expired
        if (datetime.now() - session['timestamp']).total_seconds() > 300:  # 5 minutes
            logger.error(f"Session expired for chat_id {chat_id}")
            database.remove_auth_session(chat_id)
            message = "❌ Your authorization session has expired. Please use /connect to start again."
            send_telegram_message(message, chat_id)
            return
            
        logger.info(f"Exchanging code for token for chat_id {chat_id}")
        tokens = exchange_code_for_token(code)
        
        if tokens:
            logger.info(f"Successfully exchanged code for token for chat_id {chat_id}")
            database.add_user(
                chat_id,
                tokens['access_token'],
                tokens['refresh_token'],
                tokens['expires_at']
            )
            # Remove the session after successful authentication
            database.remove_auth_session(chat_id)
            message = "✅ Your Strava account has been connected successfully!"
        else:
            logger.error(f"Failed to exchange code for token for chat_id {chat_id}")
            message = "❌ Failed to connect your Strava account. Please try again with /connect."
    except Exception as e:
        logger.error(f"Error handling auth code for chat_id {chat_id}: {str(e)}")
        message = "❌ An error occurred while connecting your account. Please try again with /connect."
    
    send_telegram_message(message, chat_id)

def send_telegram_message(message, chat_id):
    """Send a message to Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not found in .env file")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram message: {str(e)}")
        return False

def get_activities(access_token, after_ts):
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            f"https://www.strava.com/api/v3/activities?after={after_ts}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching activities: {str(e)}")
        return None

def get_activity_emoji(activity_type):
    """Get the appropriate emoji based on activity type"""
    emoji_map = {
        # Main activities
        'Ride': '🚴',
        'Run': '🏃',
        'Walk': '🚶',
        'Swim': '🏊',
        'Hike': '🥾',
        'AlpineSki': '⛷️',
        'BackcountrySki': '🎿',
        'Canoeing': '🛶',
        'Crossfit': '💪',
        'EBikeRide': '🚴‍♂️',
        'Elliptical': '🏃‍♂️',
        'Golf': '⛳',
        'Handcycle': '🦽',
        'IceSkate': '⛸️',
        'InlineSkate': '🛼',
        'Kayaking': '🛶',
        'Kitesurf': '🏄‍♂️',
        'NordicSki': '⛷️',
        'RockClimbing': '🧗',
        'RollerSki': '⛷️',
        'Rowing': '🚣',
        'Snowboard': '🏂',
        'Snowshoe': '🥾',
        'StairStepper': '🏃‍♂️',
        'StandUpPaddling': '🏄‍♂️',
        'Surfing': '🏄',
        'Velomobile': '🚴',
        'WeightTraining': '🏋️',
        'Wheelchair': '🦽',
        'Windsurf': '🏄‍♂️',
        'Workout': '💪',
        'Yoga': '🧘',
        'Unknown': '🏃'  # Default emoji
    }
    return emoji_map.get(activity_type, '🏃')  # Default to running emoji if type not found

def process_activities_for_user(chat_id):
    """Process activities for a specific user"""
    try:
        user = database.get_user(chat_id)
        if not user or not user[1]:  # No access token
            return
            
        access_token = user[1]
        if datetime.now().timestamp() >= user[3]:  # Token expired
            # TODO: Implement token refresh
            return
            
        twelve_hours_ago = datetime.now() - timedelta(hours=12)
        after_ts = int(twelve_hours_ago.timestamp())
        
        activities = get_activities(access_token, after_ts)
        if not activities:
            return
            
        send_telegram_message(get_random_greeting(), chat_id)
        
        for activity in activities:
            activity_name = activity.get('name', 'Unnamed')
            activity_id = activity.get('id')
            activity_type = activity.get('type', 'Unknown')
            duration = round(activity.get('moving_time', 0) / 60, 2)
            
            emoji = get_activity_emoji(activity_type)
            cheer = get_random_cheer().format(name=activity_name)
            
            message = f"""
{emoji} <b>{cheer}</b>
{duration} minutes well spent!
"""
            send_telegram_message(message, chat_id)
            
        send_telegram_message(get_random_signoff(), chat_id)
        
    except Exception as e:
        logger.error(f"Error processing activities for user {chat_id}: {str(e)}")

def main():
    """Main function to handle Telegram updates"""
    global auth_sessions
    try:
        logger.info("Starting Strava Kudos Bot...")
        
        # Get the last update ID
        last_update_id = 0
        
        while True:
            # Get updates from Telegram
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {
                "offset": last_update_id + 1,
                "timeout": 30
            }
            
            response = requests.get(url, params=params)
            updates = response.json().get("result", [])
            
            for update in updates:
                last_update_id = update["update_id"]
                
                if "message" in update:
                    message = update["message"]
                    chat_id = str(message["chat"]["id"])
                    text = message.get("text", "")
                    
                    logger.info(f"Received message from chat_id {chat_id}: {text}")
                    
                    # Handle commands
                    if text.startswith("/"):
                        command = text.split()[0].lower()
                        logger.info(f"Handling command: {command} for chat_id {chat_id}")
                        if command == "/start":
                            handle_start(chat_id)
                        elif command == "/help":
                            handle_help(chat_id)
                        elif command == "/connect":
                            handle_connect(chat_id)
                        elif command == "/disconnect":
                            handle_disconnect(chat_id)
                        elif command == "/status":
                            handle_status(chat_id)
                    # Handle auth code
                    elif chat_id in auth_sessions:
                        logger.info(f"Processing auth code for chat_id {chat_id}")
                        handle_auth_code(chat_id, text)
                    else:
                        logger.info(f"Message not handled for chat_id {chat_id}")
            
            # Process activities for all users
            for chat_id in database.get_all_users():
                process_activities_for_user(chat_id)
                
            # Clean up expired auth sessions
            current_time = datetime.now()
            auth_sessions = {
                chat_id: session for chat_id, session in auth_sessions.items()
                if (current_time - session['timestamp']).total_seconds() < 300  # 5 minutes
            }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()
