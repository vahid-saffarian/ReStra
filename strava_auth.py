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

def get_strava_auth_url():
    """Generate the Strava OAuth authorization URL for user authentication"""
    if not all([STRAVA_CLIENT_ID, STRAVA_REDIRECT_URI]):
        logger.error("Missing required environment variables for Strava auth")
        return None
    
    # URL encode the redirect URI
    encoded_redirect_uri = quote_plus(STRAVA_REDIRECT_URI)
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={encoded_redirect_uri}&approval_prompt=force&scope=activity:read_all"
    
    logger.info(f"Generated auth URL with redirect_uri: {STRAVA_REDIRECT_URI}")
    return auth_url

def exchange_code_for_token(code):
    """Exchange user's authorization code for their access token"""
    if not all([STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI, code]):
        logger.error("Missing required parameters for token exchange")
        return None
        
    try:
        # Log the request parameters (excluding client secret for security)
        logger.info(f"Attempting token exchange with client_id={STRAVA_CLIENT_ID}, redirect_uri={STRAVA_REDIRECT_URI}")
        
        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': STRAVA_CLIENT_ID,
                'client_secret': STRAVA_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': STRAVA_REDIRECT_URI
            }
        )
        
        # If the request fails, log the response content
        if not response.ok:
            logger.error(f"Token exchange failed with status {response.status_code}")
            logger.error(f"Response content: {response.text}")
            response.raise_for_status()
            
        return response.json()
    except requests.exceptions.RequestException as e:
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

def get_strava_header(access_token):
    """Return the authorization header for Strava API requests using user's token"""
    return {"Authorization": f"Bearer {access_token}"}

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
