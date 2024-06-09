from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters
from telegram import Update
from telegram.ext import ApplicationBuilder
from crewai_tools import tool
from dotenv import load_dotenv
from agents import conversational_agent
from crewai import Task, Crew, Process
from openai_assistants import send_initial_onboarding_message, send_follow_up_onboarding_message, get_json_data_from_last_onboarding_message
from db import _db
import time, json, pprint

from apify_scrapers import scrape_linkedin_profile
from db import _db
import os
import re

def escape_markdown_v2(text):
    # Define the characters to be escaped
    escape_chars = r'`_*[]()~>#+-=|{}.!'
    # Use regular expression to escape each character with a preceding backslash
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


load_dotenv()

TOKEN = os.getenv('TELEGRAM_API_KEY')

session_data = {}

# @tool("get_response")
# async def get_response(question):
#     """The mechanism to get the user's response. Takes in a question and returns the user's response."""
#     print(question)
#     # print(question)
#     # await context.bot.send_message(chat_id=update.effective_chat.id, text=question)
#     # return "hello"
#     value = input("Enter your response: ")
#     # value = input("Enter your response: ")
#     return value




class Bot:
    def __init__(self, token):
        self.token = token
        self.bot = ApplicationBuilder().token(TOKEN).build()

    async def start(self, update: Update, context: CallbackContext):
        session_data[update.effective_user.id] = {}
        await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Hello! I am your ATL Tech Week Assistant. Before we get started, please give me the link to your LinkedIn profile."), parse_mode="MarkdownV2")

    async def on_board(self, update: Update, context: CallbackContext):
        message, thread_id = send_initial_onboarding_message()
        if message:
            if update.effective_user.id not in session_data:
                session_data[update.effective_user.id] = {}
            session_data[update.effective_user.id]["is_onboarding"] = True
            session_data[update.effective_user.id]["thread_id"] = thread_id
            await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2(message),  parse_mode="MarkdownV2")

    async def end_onboarding(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if user_id in session_data and session_data[user_id].get("is_onboarding"):
            session_data[user_id]["is_onboarding"] = False
            json_data = get_json_data_from_last_onboarding_message(session_data[user_id]["thread_id"])
            pprint.pprint(json_data)
            if json_data:
                json_data["user_id"] = user_id
                # update the user in the database with the onboarding data
                if _db.update_user(json_data):
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Thank you! Your ATL Tech Week Profile has been successfully created."),  parse_mode="MarkdownV2")
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Sorry, there was an error processing your onboarding data. Please retry."),  parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Sorry, you are not currently in the onboarding process."),  parse_mode="MarkdownV2")

    async def handle_text_message(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        message = update.message.text
        # check if the message is a valid linkedin profile link
        if "linkedin.com/in/" in message:
            print("Scraping LinkedIn profile...")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Scraping LinkedIn profile..."),  parse_mode="MarkdownV2")
            # scrape the linkedin profile
            profile_data = scrape_linkedin_profile(message)
            # save user_id and chat_id to the profile_data
            profile_data["user_id"] = user_id
            profile_data["chat_id"] = update.effective_chat.id
            print("Saving profile data...")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Saving profile data..."),  parse_mode="MarkdownV2")
            # save the profile_data to the database
            if _db.submit_user(profile_data):
                # update the user in the database with the scraped data
                await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Thank you! Your LinkedIn profile has been successfully linked."),  parse_mode="MarkdownV2")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Now, let's chat for a bit so I know how to plan your ATL Tech Week experience! type /on_board to begin the process."), parse_mode="MarkdownV2")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Sorry, there was an error linking your LinkedIn profile."), parse_mode="MarkdownV2")
        # check if the user is in the onboarding process
        if user_id in session_data and session_data[user_id].get("is_onboarding"):
            # get the user's response
            response = message
            # send the response to the assistant
            message = send_follow_up_onboarding_message(session_data[user_id]["thread_id"], response)
            if message:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2(message), parse_mode="MarkdownV2")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=escape_markdown_v2("Sorry, there was an error processing your response. Please retry."), parse_mode="MarkdownV2")
        else:
            pass

    

    def run(self):
        self.bot.add_handler(CommandHandler('start', self.start))
        self.bot.add_handler(CommandHandler('on_board', self.on_board))
        self.bot.add_handler(CommandHandler('end_onboarding', self.end_onboarding))
        # add a message handler with a filter for when user submits their linkedin profile link
        self.bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_text_message))
        self.bot.run_polling()

if __name__ == '__main__':
    bot = Bot(TOKEN)
    bot.run()