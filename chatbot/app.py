from flask import Flask
from dapr.clients import DaprClient
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import os

app = Flask(__name__)

def main():
    telegram_access_token = os.environ.get('TELEGRAM_ACCESS_TOKEN')
    updater = Updater(token=telegram_access_token, use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), invoke_openai_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))

    updater.start_polling()
    updater.idle()

# Define a few command handlers. These usually take the two arguments update and context.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello_command(update: Update, context: CallbackContext) -> None:
    name = context.args[0]
    update.message.reply_text(f'Good day, {name}!')

def invoke_openai_chatgpt(update: Update, context: CallbackContext):
    message = update.message.text
    try:
        with DaprClient() as d:
            app_id = "openai"
            method_name = "chat"
            response = d.invoke_method(app_id=app_id, method_name=method_name, data=json.dumps({'message': message}), http_verb="POST")
            reply_message = response.text()
    except Exception as e:
            reply_message = f"Failed to call the openai chat service: {str(e)}"

    reply_message = json.loads(reply_message)["message"]
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

@app.route('/')
def hello():
    # This endpoint still exists to handle HTTP requests to Microservice A
    return "Microservice A is running and ready to handle requests."

if __name__ == '__main__':
    # Invoke the function directly before starting the Flask app
    main()

    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
