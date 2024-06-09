from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('TELEGRAM_API_KEY')

class Bot:
    def __init__(self, token):
        self.token = token
        self.bot = ApplicationBuilder().token(TOKEN).build()

    async def start(self, update: Update, context: CallbackContext):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, I'm your Telegram bot!")

    def run(self):
        self.bot.add_handler(CommandHandler('start', self.start))
        self.bot.run_polling()

if __name__ == '__main__':
    bot = Bot(TOKEN)
    bot.run()