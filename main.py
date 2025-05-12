import os
import requests
import time
import logging
import random
import tracemalloc
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from strava_auth import get_strava_header, exchange_code_for_token, get_authorization_url
import database
import telegram

# Enable tracemalloc
tracemalloc.start()

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

async def handle_start(bot, update):
    """Handle the /start command"""
    try:
        chat_id = update['message']['chat']['id']
        logger.info(f"Handling start command for chat_id {chat_id}")

        message = """
Welcome to the Strava Kudos Bot! 🏃‍♂️

To get started:
1. Use /connect to link your Strava account
2. Once connected, you'll receive kudos for your activities automatically!

Use /help to see all available commands.
"""
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Successfully sent start message to user {chat_id}")

    except Exception as e:
        logger.error(f"Error in handle_start: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error processing your request. Please try again later."
            )

async def handle_help(bot, update):
    """Handle the /help command"""
    try:
        chat_id = update['message']['chat']['id']
        logger.info(f"Handling help command for chat_id {chat_id}")

        help_text = """
🤖 *Strava Kudos Bot Help*

*Available Commands:*
/connect - Connect your Strava account
/disconnect - Disconnect your Strava account
/status - Check your connection status
/help - Show this help message

*How to Connect:*
1. Use /connect to start the authorization process
2. Click the authorization link
3. Authorize the bot on Strava
4. Copy the authorization code
5. Send the code back to the bot

*Need Help?*
If you encounter any issues, try disconnecting and reconnecting your account using /disconnect and /connect.
"""
        await bot.send_message(
            chat_id=chat_id,
            text=help_text,
            parse_mode='Markdown'
        )
        logger.info(f"Successfully sent help message to user {chat_id}")

    except Exception as e:
        logger.error(f"Error in handle_help: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error showing the help message. Please try again later."
            )

async def handle_connect(bot, update):
    """Handle the /connect command"""
    try:
        chat_id = update['message']['chat']['id']
        logger.info(f"Handling connect command for chat_id {chat_id}")
        
        # Check if user already has an active session
        session = database.get_auth_session(chat_id)
        if session:
            logger.info(f"User {chat_id} has an active session")
            await bot.send_message(
                chat_id=chat_id,
                text="You already have an active authorization session. Please complete the current authorization process or wait for it to expire."
            )
            return

        # Check if user is already connected
        user = database.get_user(chat_id)
        if user:
            logger.info(f"User {chat_id} is already connected")
            await bot.send_message(
                chat_id=chat_id,
                text="You are already connected to Strava. Use /disconnect to remove the connection first."
            )
            return

        # Generate authorization URL
        auth_url = get_authorization_url()
        if not auth_url:
            logger.error("Failed to generate authorization URL")
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error generating the authorization URL. Please try again later."
            )
            return

        # Create auth session
        state = os.urandom(16).hex()
        timestamp = datetime.now()
        if not database.add_auth_session(chat_id, state, timestamp):
            logger.error(f"Failed to create auth session for {chat_id}")
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error creating your authorization session. Please try again later."
            )
            return

        # Send authorization URL to user
        await bot.send_message(
            chat_id=chat_id,
            text=f"Please click the link below to authorize the bot to access your Strava account:\n\n{auth_url}\n\nAfter authorizing, you'll be redirected to a page with an authorization code. Copy that code and send it back to me."
        )
        logger.info(f"Sent authorization URL to user {chat_id}")

    except Exception as e:
        logger.error(f"Error in handle_connect: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error processing your request. Please try again later."
            )

async def handle_disconnect(bot, update):
    """Handle the /disconnect command"""
    try:
        chat_id = update['message']['chat']['id']
        logger.info(f"Handling disconnect command for chat_id {chat_id}")

        # Check if user is connected
        user = database.get_user(chat_id)
        if not user:
            logger.info(f"User {chat_id} is not connected")
            await bot.send_message(
                chat_id=chat_id,
                text="You are not connected to Strava. Use /connect to connect your account."
            )
            return

        # Remove user data
        if not database.remove_user(chat_id):
            logger.error(f"Failed to remove user data for {chat_id}")
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error disconnecting your account. Please try again later."
            )
            return

        # Send success message
        await bot.send_message(
            chat_id=chat_id,
            text="✅ Successfully disconnected from Strava. Use /connect to connect your account again."
        )
        logger.info(f"Successfully disconnected user {chat_id} from Strava")

    except Exception as e:
        logger.error(f"Error in handle_disconnect: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error processing your request. Please try again later."
            )

async def handle_status(bot, update):
    """Handle the /status command"""
    try:
        chat_id = update['message']['chat']['id']
        logger.info(f"Handling status command for chat_id {chat_id}")

        # Check if user is connected
        user = database.get_user(chat_id)
        if not user:
            logger.info(f"User {chat_id} is not connected")
            await bot.send_message(
                chat_id=chat_id,
                text="You are not connected to Strava. Use /connect to connect your account."
            )
            return

        # Check if token is expired
        expires_at = datetime.fromisoformat(user['expires_at'])
        if datetime.now() >= expires_at:
            logger.info(f"Token expired for user {chat_id}")
            await bot.send_message(
                chat_id=chat_id,
                text="Your Strava connection has expired. Use /connect to reconnect your account."
            )
            return

        # Send status message
        await bot.send_message(
            chat_id=chat_id,
            text="✅ Your Strava account is connected and active."
        )
        logger.info(f"Successfully sent status to user {chat_id}")

    except Exception as e:
        logger.error(f"Error in handle_status: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error checking your status. Please try again later."
            )

async def handle_auth_code(bot, update):
    """Handle the authorization code from the user"""
    try:
        chat_id = update['message']['chat']['id']
        code = update['message']['text']
        logger.info(f"Handling auth code for chat_id {chat_id}")

        # Check if user has an active session
        session = database.get_auth_session(chat_id)
        if not session:
            logger.info(f"No active session found for {chat_id}")
            await bot.send_message(
                chat_id=chat_id,
                text="No active authorization session found. Please use /connect to start the authorization process."
            )
            return

        # Check if session has expired
        if datetime.now() - session['timestamp'] > timedelta(minutes=5):
            logger.info(f"Session expired for {chat_id}")
            database.remove_auth_session(chat_id)
            await bot.send_message(
                chat_id=chat_id,
                text="Your authorization session has expired. Please use /connect to start a new session."
            )
            return

        # Exchange code for tokens
        tokens = exchange_code_for_token(code)
        if not tokens:
            logger.error(f"Failed to exchange code for tokens for {chat_id}")
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error exchanging the authorization code. Please try again with /connect."
            )
            return

        # Store user data
        if not database.add_user(chat_id, tokens['access_token'], tokens['refresh_token'], tokens['expires_at']):
            logger.error(f"Failed to store user data for {chat_id}")
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error storing your connection. Please try again with /connect."
            )
            return

        # Clean up session
        database.remove_auth_session(chat_id)

        # Send success message
        await bot.send_message(
            chat_id=chat_id,
            text="✅ Successfully connected to Strava! You can now use the bot to interact with your Strava account."
        )
        logger.info(f"Successfully connected user {chat_id} to Strava")

    except Exception as e:
        logger.error(f"Error in handle_auth_code: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            await bot.send_message(
                chat_id=chat_id,
                text="Sorry, there was an error processing your authorization code. Please try again with /connect."
            )

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

async def process_update(update):
    """Process a single update from webhook"""
    try:
        if "message" in update:
            message = update["message"]
            chat_id = str(message["chat"]["id"])
            text = message.get("text", "")
            
            logger.info(f"Processing message - chat_id: {chat_id}, text: {text}")
            
            # Create bot instance for this update
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            
            # Handle commands
            if text.startswith("/"):
                command = text.split()[0].lower()
                logger.info(f"Handling command: {command} for chat_id {chat_id}")
                if command == "/start":
                    await handle_start(bot, update)
                elif command == "/help":
                    await handle_help(bot, update)
                elif command == "/connect":
                    await handle_connect(bot, update)
                elif command == "/disconnect":
                    await handle_disconnect(bot, update)
                elif command == "/status":
                    await handle_status(bot, update)
            # Handle auth code
            elif database.get_auth_session(chat_id):
                logger.info(f"Processing auth code for chat_id {chat_id}")
                await handle_auth_code(bot, update)
            else:
                logger.info(f"Message not handled for chat_id {chat_id}")

    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
