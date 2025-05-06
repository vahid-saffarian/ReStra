import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

def refresh_access_token():
    try:
        print("Attempting to refresh access token...")
        print(f"Using Client ID: {CLIENT_ID}")
        print(f"Using Refresh Token: {REFRESH_TOKEN[:5]}...")  # Only print first 5 chars for security
        
        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": REFRESH_TOKEN,
            },
        )
        
        if response.status_code == 400:
            print("❌ Bad Request - Your refresh token might be invalid or expired")
            print("Please get a new refresh token from Strava")
            return None
            
        response.raise_for_status()
        tokens = response.json()
        print("✅ Access token refreshed successfully")
        return tokens["access_token"]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error refreshing token: {str(e)}")
        return None

def get_strava_header():
    """
    Returns the authorization header for Strava API requests
    """
    access_token = refresh_access_token()
    if not access_token:
        print("❌ Failed to get access token")
        return None
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
