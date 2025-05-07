from flask import Flask, request, render_template_string
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log the loaded environment variables
logger.info(f"Loaded environment variables - Redirect URI: {os.getenv('STRAVA_REDIRECT_URI')}")

app = Flask(__name__)

# HTML template for the success page
SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Strava Authorization Success</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            text-align: center;
        }
        .code-box {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 16px;
            cursor: pointer;
        }
        .instructions {
            color: #666;
            margin: 20px 0;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>✅ Authorization Successful!</h1>
    <div class="instructions">
        <p>Your Strava authorization code is:</p>
    </div>
    <div class="code-box" onclick="copyCode()" id="codeBox">
        {{ code }}
    </div>
    <div class="instructions">
        <p>Click the code above to copy it, then paste it in your Telegram chat with the bot.</p>
    </div>
    <button class="button" onclick="copyCode()">Copy Code</button>

    <script>
        function copyCode() {
            const codeBox = document.getElementById('codeBox');
            const textArea = document.createElement('textarea');
            textArea.value = codeBox.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            const button = document.querySelector('.button');
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    logger.info(f"Received callback with code: {code}, state: {state}, error: {error}")
    
    if error:
        logger.error(f"Authorization error: {error}")
        return f"Authorization error: {error}"
        
    if code:
        logger.info("Successfully received authorization code")
        return render_template_string(SUCCESS_TEMPLATE, code=code)
        
    logger.error("No authorization code received")
    return "No authorization code received."

# For local development
if __name__ == '__main__':
    app.run(port=4040) 