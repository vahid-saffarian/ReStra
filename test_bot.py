import os
from dotenv import load_dotenv
import requests
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_telegram_bot():
    """Test if the Telegram bot token is valid"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        return False
        
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        response.raise_for_status()
        bot_info = response.json()
        if bot_info.get('ok'):
            logger.info(f"✅ Telegram bot is working! Bot name: @{bot_info['result']['username']}")
            return True
        else:
            logger.error("❌ Invalid Telegram bot token")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing Telegram bot: {str(e)}")
        return False

def test_strava_api():
    """Test if the Strava API credentials are valid"""
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    redirect_uri = os.getenv('STRAVA_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        logger.error("❌ Missing Strava API credentials in .env file")
        return False
        
    try:
        # Test the authorization URL
        auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope=activity:read_all"
        logger.info(f"✅ Strava authorization URL generated: {auth_url}")
        return True
    except Exception as e:
        logger.error(f"❌ Error testing Strava API: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting bot tests...")
    
    # Test Telegram bot
    telegram_ok = test_telegram_bot()
    
    # Test Strava API
    strava_ok = test_strava_api()
    
    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"Telegram Bot: {'✅ OK' if telegram_ok else '❌ Failed'}")
    logger.info(f"Strava API: {'✅ OK' if strava_ok else '❌ Failed'}")
    
    if telegram_ok and strava_ok:
        logger.info("\n✅ All tests passed! You can now run the bot with: python main.py")
    else:
        logger.info("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 