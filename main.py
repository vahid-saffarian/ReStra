import os
import requests
import time
import logging
import random
import tracemalloc
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from strava_auth import get_strava_header, exchange_code_for_token, get_authorization_url, refresh_access_token
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
Welcome to the restra Bot! 🏃‍♂️

To get started:
1. Use /connect to link your Strava account
2. Once connected, we'll be chatting about your activities!

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
🤖 *restra Bot Help*

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

        # Check if user has an active session
        session = database.get_auth_session(chat_id)
        if session:
            logger.info(f"User {chat_id} has an active session: {session}")
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
        logger.info(f"Creating auth session for {chat_id} with state {state} at {timestamp}")
        
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

        # Get expiration time (it's already a datetime object)
        expires_at = user['expires_at']
        
        # Check if token has expired
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
        logger.info(f"Sent active status message to user {chat_id}")

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
    """Process activities for a specific user (suitable for a periodic job)."""
    try:
        logger.info(f"Periodic check: Attempting to process activities for user {chat_id}.")
        user = database.get_user(chat_id) # Fetches from Redis, returns a dict or None

        if not user:
            logger.info(f"Periodic check: User {chat_id} not found or not connected. Skipping.")
            return

        # Gracefully access user data
        access_token = user.get('access_token')
        refresh_token = user.get('refresh_token')
        expires_at = user.get('expires_at') # This should be a datetime object from database.get_user()

        if not all([access_token, refresh_token, expires_at]):
            logger.error(f"Periodic check: User {chat_id} data is incomplete. access_token: {'found' if access_token else 'missing'}, refresh_token: {'found' if refresh_token else 'missing'}, expires_at: {'found' if expires_at else 'missing'}. Skipping.")
            return

        # Ensure expires_at is a datetime object (it should be, but defensive check)
        if not isinstance(expires_at, datetime):
            logger.error(f"Periodic check: User {chat_id} expires_at is not a datetime object: {type(expires_at)}. Skipping.")
            # Potentially try to parse it if it's a string, or log an error and return
            return


        # Check if token has expired or will expire soon (e.g., within 15 minutes)
        if datetime.now() >= expires_at - timedelta(minutes=15):
            logger.info(f"Periodic check: Token for user {chat_id} (expires at {expires_at}) is expired or expiring soon. Refreshing...")
            
            new_tokens = refresh_access_token(refresh_token)

            if new_tokens and 'access_token' in new_tokens and 'expires_in' in new_tokens:
                logger.info(f"Periodic check: Successfully refreshed token for user {chat_id}.")
                access_token = new_tokens['access_token'] # Use the new token for this run
                
                # Calculate new expiration datetime object
                new_expires_at_timestamp = datetime.now().timestamp() + new_tokens['expires_in']
                new_expires_at_datetime = datetime.fromtimestamp(new_expires_at_timestamp)
                
                # Update user data in Redis with new tokens and expiry
                database.add_user(
                    chat_id,
                    new_tokens['access_token'],
                    new_tokens.get('refresh_token', refresh_token), # Use new refresh token if Strava provides it
                    new_expires_at_datetime # Pass the datetime object
                )
                expires_at = new_expires_at_datetime # Update expires_at for current run if needed, though not strictly necessary here
            else:
                logger.error(f"Periodic check: Failed to refresh token for user {chat_id}. Response: {new_tokens}. Notifying user.")
                send_telegram_message(
                    "⚠️ Your Strava connection needs to be refreshed, but it failed. Please try /disconnect and /connect again.",
                    str(chat_id) # Ensure chat_id is a string if send_telegram_message expects it
                )
                return # Cannot proceed without a valid token

        # Fetch activities from the last 12 hours
        twelve_hours_ago = datetime.now() - timedelta(minutes=1)
        after_ts = int(twelve_hours_ago.timestamp())
        
        logger.info(f"Periodic check: Fetching activities for user {chat_id} after timestamp {after_ts}.")
        activities = get_activities(access_token, after_ts) # Assumes get_activities is synchronous
        
        if activities is None: 
            logger.error(f"Periodic check: Failed to fetch activities for user {chat_id}. An error occurred in get_activities.")
            return
        if not activities: 
            logger.info(f"Periodic check: No new activities for user {chat_id} in the last 12 hours.")
            return

        logger.info(f"Periodic check: Found {len(activities)} new activities for user {chat_id}.")
        send_telegram_message(get_random_greeting(), str(chat_id))
        
        activity_count = 0
        for activity in activities:
            activity_name = activity.get('name', 'Unnamed Activity')
            activity_type = activity.get('type', 'Unknown')
            duration_seconds = activity.get('moving_time', 0)
            duration_minutes = round(duration_seconds / 60, 2)
            
            emoji = get_activity_emoji(activity_type)
            cheer = get_random_cheer().format(name=activity_name)
            
            message = f\"\"\"
{emoji} <b>{cheer}</b>
{duration_minutes} minutes well spent!
\"\"\"
            send_telegram_message(message, str(chat_id))
            activity_count +=1
            
        send_telegram_message(f"Processed {activity_count} activities. {get_random_signoff()}", str(chat_id))
        logger.info(f"Periodic check: Processed {activity_count} activities for user {chat_id}.")

    except Exception as e:
        # Log the full traceback for unexpected errors
        logger.exception(f"Periodic check: Unexpected error processing activities for user {chat_id}: {str(e)}")

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
            else:
                session = database.get_auth_session(chat_id)
                logger.info(f"Auth session for {chat_id}: {session}")
                if session:
                    logger.info(f"Processing auth code for chat_id {chat_id}")
                    await handle_auth_code(bot, update)
                else:
                    logger.info(f"No active auth session found for chat_id {chat_id}")
                    await bot.send_message(
                        chat_id=chat_id,
                        text="No active authorization session found. Please use /connect to start the authorization process."
                    )

    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
        if 'bot' in locals() and 'chat_id' in locals():
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Sorry, there was an error processing your message. Please try again."
                )
            except Exception as send_error:
                logger.error(f"Error sending error message: {str(send_error)}")
