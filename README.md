# Strava Kudos Bot

A Telegram bot that connects to Strava and sends motivational messages based on your activities.

## Bot Setup (For Administrators)

1. **Create a Telegram Bot**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use the `/newbot` command to create a new bot
   - Save the bot token you receive

2. **Set up Strava API**
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Create a new application
   - Set the Authorization Callback Domain to your deployed server's domain
   - Save your Client ID and Client Secret
   - These credentials are only used for the OAuth flow, not for accessing user data

3. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     STRAVA_CLIENT_ID=your_strava_client_id
     STRAVA_CLIENT_SECRET=your_strava_client_secret
     STRAVA_REDIRECT_URI=https://your-deployed-server.com
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Bot**
   ```bash
   python main.py
   ```

## Deployment Options

### Option 1: Local Development with ngrok
1. Install ngrok: https://ngrok.com/download
2. Run ngrok to create a tunnel:
   ```bash
   ngrok http 4040
   ```
3. Copy the HTTPS URL provided by ngrok
4. Update your `.env` file:
   ```
   STRAVA_REDIRECT_URI=https://your-ngrok-url.ngrok.io
   ```
5. Update your Strava API settings with the ngrok URL

### Option 2: Deploy to Heroku
1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set STRAVA_CLIENT_ID=your_client_id
   heroku config:set STRAVA_CLIENT_SECRET=your_client_secret
   heroku config:set STRAVA_REDIRECT_URI=https://your-app-name.herokuapp.com
   ```
4. Deploy the app:
   ```bash
   git push heroku main
   ```

### Option 3: Deploy to Railway
1. Create a Railway account
2. Create a new project and connect your GitHub repository
3. Set the environment variables in Railway's dashboard
4. Railway will automatically deploy your app

## User Guide

1. **Start the Bot**
   - Open Telegram and find your bot
   - Send `/start` to begin

2. **Connect Your Strava Account**
   - Use `/connect` to start the Strava authentication process
   - Click the link provided
   - Log in to your Strava account
   - Authorize the bot to access your activities
   - Copy the authorization code from the browser
   - Send the code back to the bot
   - The bot will now use your Strava account credentials to access your activities

3. **Available Commands**
   - `/start` - Start the bot
   - `/help` - Show available commands
   - `/connect` - Connect your Strava account
   - `/disconnect` - Disconnect your Strava account
   - `/status` - Check your connection status

## Features

- Each user connects their own Strava account
- Automatically checks for new Strava activities
- Sends personalized motivational messages
- Supports multiple users with their own Strava accounts
- Handles token refresh automatically
- Provides activity-specific emojis and messages

## Troubleshooting

If you encounter any issues:

1. Make sure you've authorized the bot on Strava
2. Try disconnecting and reconnecting your account
3. Check if your Strava account is active
4. Contact the bot administrator if problems persist

## Contributing

Feel free to submit issues and enhancement requests! 