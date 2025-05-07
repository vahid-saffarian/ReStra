from flask import Flask, request, jsonify
import os
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application
from main import handle_auth_code, handle_connect, handle_disconnect, handle_status, handle_help

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize bot
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        update = request.get_json()
        logger.info(f"Received webhook update: {update}")
        
        if not update:
            return jsonify({"status": "error", "message": "No update received"}), 400
            
        # Extract message data
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        if not chat_id or not text:
            return jsonify({"status": "error", "message": "Invalid message format"}), 400
            
        logger.info(f"Processing message - chat_id: {chat_id}, text: {text}")
        
        # Handle commands
        if text.startswith('/'):
            command = text.split()[0].lower()
            if command == '/connect':
                handle_connect(bot, update)
            elif command == '/disconnect':
                handle_disconnect(bot, update)
            elif command == '/status':
                handle_status(bot, update)
            elif command == '/help':
                handle_help(bot, update)
        else:
            # Handle auth code
            handle_auth_code(bot, update)
            
        return jsonify({"status": "success"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 
    