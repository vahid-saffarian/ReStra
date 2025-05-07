import os
import requests
import time
import logging
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from strava_auth import get_strava_header

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strava_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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

def send_telegram_message(message):
    """Send a message to Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials not found in .env file")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
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

def main():
    try:
        logger.info("Starting Strava Kudos Bot...")
        
        # Get fresh headers with access token
        headers = get_strava_header()
        if not headers:
            error_msg = "❌ Failed to get authorization. Exiting..."
            logger.error(error_msg)
            send_telegram_message(error_msg)
            return
            
        access_token = headers["Authorization"].split(" ")[1]
        
        twelve_hours_ago = datetime.now() - timedelta(hours=12)
        after_ts = int(twelve_hours_ago.timestamp())

        activities = get_activities(access_token, after_ts)
        if not activities:
            error_msg = get_random_inspiration()
            logger.info(error_msg)
            send_telegram_message(error_msg)
            return
            
        logger.info(f"Found {len(activities)} activities since {twelve_hours_ago.isoformat()} UTC")
        send_telegram_message(get_random_greeting())
        for activity in activities:
            activity_name = activity.get('name', 'Unnamed')
            activity_id = activity.get('id')
            activity_type = activity.get('type', 'Unknown')
            distance = round(activity.get('distance', 0) / 1000, 2)
            duration = round(activity.get('moving_time', 0) / 60, 2)
            
            emoji = get_activity_emoji(activity_type)
            cheer = get_random_cheer().format(name=activity_name)
                
            message = f"""
{emoji} <b>{cheer}</b>
{duration} minutes well spent!
"""
            logger.info(f"Found activity: {activity_name} ({activity_id})")
            send_telegram_message(message)
                
        logger.info("Bot finished processing activities")
        send_telegram_message(get_random_signoff())
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        send_telegram_message(f"❌ {error_msg}")

if __name__ == "__main__":
    main()
