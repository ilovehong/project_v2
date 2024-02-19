from flask import Flask
from dapr.clients import DaprClient
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import os
from message_logger import MessageLogger

app = Flask(__name__)

# Setup database configuration for the logger
db_config = {
    'dbname': os.environ.get('POSTGRES_DATABASE'),
    'user': os.environ.get('POSTGRES_USERNAME'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST')
}

# Global variable to store the bot's ID
bot_id = None

# Initialize the logger
logger = MessageLogger(db_config)

def main():
    telegram_access_token = os.environ.get('TELEGRAM_ACCESS_TOKEN')
    updater = Updater(token=telegram_access_token, use_context=True)
    
    global bot_id
    bot_info = updater.bot.get_me()
    bot_id = bot_info.id

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), invoke_openai_chatgpt)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(chatgpt_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()

# Define a few command handlers. These usually take the two arguments update and context.
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('help command is for health check only')

def invoke_openai_chatgpt(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.message.text
    # Log the user message
    logger.log_message(user_id, message)

    try:
        with DaprClient() as d:
            app_id = "openai"
            method_name = "chat"
            response = d.invoke_method(app_id=app_id, method_name=method_name, data=json.dumps({'message': message}), http_verb="POST")
            reply_message = response.text()
    except Exception as e:
            reply_message = f"Failed to call the openai chat service: {str(e)}"

    reply_message = json.loads(reply_message)["message"]

    # Log the reply message
    global bot_id
    logger.log_message(bot_id, reply_message)

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

@app.route('/')
def hello():
    # This endpoint still exists to handle HTTP requests to Microservice A
    return "Microservice A is running and ready to handle requests."

if __name__ == '__main__':
    # Invoke the function directly before starting the Flask app
    try:
        main()
    finally:
        # Ensure the logger is closed properly when the application ends
        logger.close()

    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
