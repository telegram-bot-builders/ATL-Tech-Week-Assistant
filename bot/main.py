from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters
from telegram import Update
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv
from apify_scrapers import scrape_linkedin_profile
from db import _db
import os
load_dotenv()

TOKEN = os.getenv('TELEGRAM_API_KEY')

class Bot:
    def __init__(self, token):
        self.token = token
        self.bot = ApplicationBuilder().token(TOKEN).build()

    async def start(self, update: Update, context: CallbackContext):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am your ATL Tech Week Assistant. Before we get started, please give me the link to your LinkedIn profile.")

    async def handle_text_message(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        message = update.message.text
        # check if the message is a valid linkedin profile link
        if "linkedin.com/in/" in message:
            print("Scraping LinkedIn profile...")
            # scrape the linkedin profile
            profile_data = scrape_linkedin_profile(message)
            # save user_id and chat_id to the profile_data
            profile_data["user_id"] = user_id
            profile_data["chat_id"] = update.effective_chat.id
            print("Saving profile data...")
            # save the profile_data to the database
            if _db.submit_user(profile_data):
                # update the user in the database with the scraped data
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you! Your LinkedIn profile has been successfully linked.")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, there was an error linking your LinkedIn profile.")
        else:
            pass

    

    def run(self):
        self.bot.add_handler(CommandHandler('start', self.start))
        # add a message handler with a filter for when user submits their linkedin profile link
        self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_text_message))
        self.bot.run_polling()

if __name__ == '__main__':
    bot = Bot(TOKEN)
    bot.run()