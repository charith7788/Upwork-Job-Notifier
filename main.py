import os
import json
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
import logging
from flask import Flask, request
from threading import Thread

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv('API_KEY')
BASE_RSS_URL = 'https://www.upwork.com/ab/feed/jobs/rss?paging=NaN-undefined&q='

FEEDS_FILE = 'user_feeds.json'
LAST_UPDATE_FILE = 'last_update.json'

if os.path.exists(FEEDS_FILE):
    with open(FEEDS_FILE, 'r') as f:
        user_feeds = json.load(f)
else:
    user_feeds = {}

if os.path.exists(LAST_UPDATE_FILE):
    with open(LAST_UPDATE_FILE, 'r') as f:
        last_update_times = json.load(f)
else:
    last_update_times = {}

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "Welcome to the Upwork RSS feed bot! Here is a summary of the available commands:\n\n"
        "/add <search keyword>\n"
        "Example: /add autocad\n"
        "Adds a new search keyword to your list.\n\n"
        "/view\n"
        "Example: /view\n"
        "Shows the list of your current search keywords.\n\n"
        "/edit <index> <search keyword>\n"
        "Example: /edit 1 autocad\n"
        "Edits an existing search keyword by specifying the index and new keyword.\n\n"
        "/remove <index>\n"
        "Example: /remove 1\n"
        "Removes a search keyword by specifying the index.\n\n"
        "/help\n"
        "Shows this help message."
    )
    update.message.reply_text(welcome_text)

def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Available commands and their usage:\n\n"
        "/add <search keyword>\n"
        "Example: /add autocad\n"
        "Adds a new search keyword to your list.\n\n"
        "/view\n"
        "Example: /view\n"
        "Shows the list of your current search keywords.\n\n"
        "/edit <index> <search keyword>\n"
        "Example: /edit 1 autocad\n"
        "Edits an existing search keyword by specifying the index and new keyword.\n\n"
        "/remove <index>\n"
        "Example: /remove 1\n"
        "Removes a search keyword by specifying the index.\n\n"
        "/help\n"
        "Shows this help message."
    )
    update.message.reply_text(help_text)

def add_search(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    search_keyword = ' '.join(context.args)
    rss_url = BASE_RSS_URL + search_keyword.replace(' ', '%20')
    if user_id not in user_feeds:
        user_feeds[user_id] = []
    user_feeds[user_id].append(rss_url)
    last_update_times[user_id] = {rss_url: datetime.now().isoformat()}
    update.message.reply_text(f'Added search keyword: {search_keyword}')
    save_feeds()

def edit_search(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    if len(context.args) != 2:
        update.message.reply_text('Usage: /edit <index> <search keyword>')
        return
    try:
        index = int(context.args[0])
        new_keyword = context.args[1]
        new_url = BASE_RSS_URL + new_keyword.replace(' ', '%20')
        if user_id in user_feeds and 0 <= index < len(user_feeds[user_id]):
            old_url = user_feeds[user_id][index]
            user_feeds[user_id][index] = new_url
            last_update_times[user_id][new_url] = datetime.now().isoformat()
            if old_url in last_update_times[user_id]:
                del last_update_times[user_id][old_url]
            update.message.reply_text(f'Edited search keyword at index {index}: {new_keyword}')
            save_feeds()
        else:
            update.message.reply_text('Invalid index.')
    except ValueError:
        update.message.reply_text('Usage: /edit <index> <search keyword>')

def remove_rss(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    if len(context.args) != 1:
        update.message.reply_text('Usage: /remove <index>')
        return
    try:
        index = int(context.args[0])
        if user_id in user_feeds and 0 <= index < len(user_feeds[user_id]):
            removed_feed = user_feeds[user_id].pop(index)
            if removed_feed in last_update_times[user_id]:
                del last_update_times[user_id][removed_feed]
            update.message.reply_text(f'Removed search keyword at index {index}')
            save_feeds()
        else:
            update.message.reply_text('Invalid index.')
    except ValueError:
        update.message.reply_text('Usage: /remove <index>')

def view_rss(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    if user_id in user_feeds and user_feeds[user_id]:
        feeds_list = "\n".join([f"{i}: {url.split('=')[-1].replace('%20', ' ')}" for i, url in enumerate(user_feeds[user_id])])
        update.message.reply_text(f"Your search keywords:\n{feeds_list}")
    else:
        update.message.reply_text('You have no search keywords.')

def fetch_feeds(context: CallbackContext):
    for user_id, feeds in user_feeds.items():
        if user_id not in last_update_times:
            last_update_times[user_id] = {}
        for feed_url in feeds:
            last_update_time = datetime.fromisoformat(last_update_times[user_id].get(feed_url, '1970-01-01T00:00:00'))
            try:
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning(f'Failed to parse feed URL: {feed_url}')
                    continue
                if feed.entries:
                    latest_entry = feed.entries[0]
                    updated_time = datetime(*latest_entry.published_parsed[:6])
                    if updated_time > last_update_time:
                        title = latest_entry.title
                        description = latest_entry.description

                        soup = BeautifulSoup(description, "html.parser")
                        description_text = soup.get_text(separator="\n")

                        link = latest_entry.link
                        message = f"<b>New job posted:</b>\n\n<b>{title}</b>\n\n{description_text}\n\n"

                        button = InlineKeyboardButton(text="View Job", url=link)
                        reply_markup = InlineKeyboardMarkup([[button]])
                        context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode="HTML")
                        last_update_times[user_id][feed_url] = updated_time.isoformat()
            except Exception as e:
                logger.error(f'Error fetching feed {feed_url}: {e}')
    save_last_update_times()

def save_feeds():
    with open(FEEDS_FILE, 'w') as f:
        json.dump(user_feeds, f)

def save_last_update_times():
    with open(LAST_UPDATE_FILE, 'w') as f:
        json.dump(last_update_times, f)

# Flask server setup
app = Flask(__name__)

@app.route(f'/{API_KEY}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'Upwork Job Notifier Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    bot = Bot(token=API_KEY)
    dispatcher = Dispatcher(bot, None, use_context=True)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add_search))
    dispatcher.add_handler(CommandHandler("edit", edit_search))
    dispatcher.add_handler(CommandHandler("remove", remove_rss))
    dispatcher.add_handler(CommandHandler("view", view_rss))

    # Set up the Flask server in a separate thread
    server_thread = Thread(target=run_flask)
    server_thread.start()

    # Set the webhook
    bot.set_webhook(url=f"https://upwork-job-notifier.onrender.com/{API_KEY}")

    job_queue = updater.job_queue
    job_queue.run_repeating(fetch_feeds, interval=300, first=0)
