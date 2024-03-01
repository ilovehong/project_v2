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

# Initialize the logger
logger = MessageLogger(db_config)

def main():
    updater = Updater(token=os.environ.get('TELEGRAM_ACCESS_TOKEN'), use_context=True)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), invoke_openai_chatgpt)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(chatgpt_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("mark", mark_command))

    updater.start_polling()
    updater.idle()

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

    parsed_message = json.loads(reply_message)
    for key, value in parsed_message.items():
        if key == "answer":
            context.bot.send_message(chat_id=update.effective_chat.id, text=value)
        elif key == "sources":
            template = "{}: {}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=template.format(key, value))

# Define a few command handlers. These usually take the two arguments update and context.
def mark_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    message = update.message.text
    # Log the user message
    logger.log_message(user_id, message)

    try:
        with DaprClient() as d:
            app_id = "openai"
            method_name = "mark"
            response = d.invoke_method(app_id=app_id, method_name=method_name, data=json.dumps({'message': message}), http_verb="POST")
            reply_message = response.text()
    except Exception as e:
            reply_message = f"Failed to call the openai chat service: {str(e)}"

    parsed_message = json.loads(reply_message)
    for key, value in parsed_message.items():
        if key == "feedback":
            context.bot.send_message(chat_id=update.effective_chat.id, text=value)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Ask me anything about HKBU course or /mark to get feedback on essay')

@app.route('/')
def hello():
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
