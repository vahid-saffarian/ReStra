import os
import requests
import time
import logging
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
            error_msg = "😏 lace up your shoes and get out there!"
            logger.info(error_msg)
            send_telegram_message(error_msg)
            return
            
        logger.info(f"Found {len(activities)} activities since {twelve_hours_ago.isoformat()} UTC")

        for activity in activities:
            activity_name = activity.get('name', 'Unnamed')
            activity_id = activity.get('id')
            activity_type = activity.get('type', 'Unknown')
            distance = round(activity.get('distance', 0) / 1000, 2)
            duration = round(activity.get('moving_time', 0) / 60, 2)
                
            message = f"""
🏃 <b>Kudos to {activity_name}!</b>
{duration} minutes well spent!
"""
            logger.info(f"Found activity: {activity_name} ({activity_id})")
            send_telegram_message(message)
                
        logger.info("Bot finished processing activities")
        send_telegram_message("See you l8r 🐊")
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        send_telegram_message(f"❌ {error_msg}")

if __name__ == "__main__":
    main()
