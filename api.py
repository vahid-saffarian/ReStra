from flask import Flask, request, jsonify
import os
import logging
from dotenv import load_dotenv
from main import handle_start, handle_help, handle_connect, handle_disconnect, handle_status, handle_auth_code, send_telegram_message

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram webhook updates"""
    try:
        update = request.json
        logger.info(f"Received webhook update: {update}")
        
        if "message" in update:
            message = update["message"]
            chat_id = str(message["chat"]["id"])
            text = message.get("text", "")
            
            logger.info(f"Processing message from chat_id {chat_id}: {text}")
            
            # Handle commands
            if text.startswith("/"):
                command = text.split()[0].lower()
                logger.info(f"Handling command: {command} for chat_id {chat_id}")
                if command == "/start":
                    handle_start(chat_id)
                elif command == "/help":
                    handle_help(chat_id)
                elif command == "/connect":
                    handle_connect(chat_id)
                elif command == "/disconnect":
                    handle_disconnect(chat_id)
                elif command == "/status":
                    handle_status(chat_id)
            # Handle auth code
            elif chat_id in auth_sessions:
                logger.info(f"Processing auth code for chat_id {chat_id}")
                handle_auth_code(chat_id, text)
            else:
                logger.info(f"Message not handled for chat_id {chat_id}")
        
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    """Home route for health check"""
    return "Strava Kudos Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 