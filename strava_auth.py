import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot's Strava API credentials (only used for OAuth flow)
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REDIRECT_URI = os.getenv('STRAVA_REDIRECT_URI')

# Log the loaded environment variables (excluding secret)
logger.info(f"Loaded environment variables - Client ID: {STRAVA_CLIENT_ID}, Redirect URI: {STRAVA_REDIRECT_URI}")

def get_authorization_url():
    """Generate the Strava authorization URL"""
    try:
        if not STRAVA_CLIENT_ID or not STRAVA_REDIRECT_URI:
            logger.error("Missing required environment variables for authorization URL")
            return None

        auth_url = (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={STRAVA_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={STRAVA_REDIRECT_URI}"
            f"&approval_prompt=force"
            f"&scope=read,activity:read"
        )
        logger.info(f"Generated authorization URL with redirect URI: {STRAVA_REDIRECT_URI}")
        return auth_url
    except Exception as e:
        logger.error(f"Error generating authorization URL: {str(e)}")
        return None

def get_strava_header(access_token):
    """Get the header for Strava API requests"""
    return {"Authorization": f"Bearer {access_token}"}

def exchange_code_for_token(code):
    """Exchange the authorization code for access and refresh tokens"""
    try:
        if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET or not STRAVA_REDIRECT_URI:
            logger.error("Missing required environment variables for token exchange")
            return None

        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": STRAVA_CLIENT_ID,
                "client_secret": STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Calculate token expiration
        expires_in = data.get('expires_in', 21600) # Default to 6 hours
        expires_at_timestamp = datetime.now().timestamp() + expires_in
        expires_at_datetime = datetime.fromtimestamp(expires_at_timestamp)
        
        logger.info(f"Token expires at: {expires_at_datetime}")
        
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_at': expires_at_datetime # Return datetime object
        }
    except Exception as e:
        logger.error(f"Error exchanging code for token: {str(e)}")
        return None

def refresh_access_token(refresh_token):
    """Refresh user's expired access token"""
    if not all([STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, refresh_token]):
        logger.error("Missing required parameters for token refresh")
        return None
        
    try:
        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': STRAVA_CLIENT_ID,
                'client_secret': STRAVA_CLIENT_SECRET,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return None

# Test the connection
if __name__ == "__main__":
    headers = get_strava_header()
    if headers:
        try:
            response = requests.get(
                "https://www.strava.com/api/v3/athlete/activities",
                headers=headers
            )
            response.raise_for_status()
            print("✅ Successfully connected to Strava API")
            activities = response.json()
            print(f"Found {len(activities)} activities")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing Strava API: {str(e)}")
    else:
        print("❌ Could not get authorization header")
