# Strava Kudos Bot

A GitHub Actions-powered bot that automatically checks for new Strava activities and sends notifications via Telegram.

## Features

- Runs every 12 hours automatically
- Checks for new Strava activities
- Sends notifications via Telegram
- Can be manually triggered from GitHub UI

## Setup

1. Fork this repository

2. Add the following secrets to your repository (Settings > Secrets and variables > Actions):
   - `STRAVA_CLIENT_ID`: Your Strava API client ID
   - `STRAVA_CLIENT_SECRET`: Your Strava API client secret
   - `STRAVA_REFRESH_TOKEN`: Your Strava refresh token
   - `STRAVA_ACCESS_TOKEN`: Your Strava access token
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID

3. Enable GitHub Actions in your repository (Actions tab > Enable Actions)

## Manual Trigger

You can manually trigger the bot from the Actions tab in your repository:
1. Go to the Actions tab
2. Select "Strava Bot" workflow
3. Click "Run workflow"

## Logs

The bot logs its activity to the GitHub Actions logs. You can view these logs in the Actions tab of your repository.

## Local Development

To run the bot locally:

1. Clone the repository
2. Create a `.env` file with the same secrets as above
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python main.py
   ``` 