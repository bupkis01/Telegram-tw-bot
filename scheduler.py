# scheduler.py
# Main loop: scrape accounts and send new tweets to Telegram,
# with an initial eager post for top-3 priority accounts.

import os
import time
import json
import traceback
import schedule
import snscrape.modules.twitter as sntwitter
import telebot
from urllib.parse import urlparse

import config
from formatter import format_message
from helper import download_media, extract_media_urls

# Initialize Telegram bot
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)

# Load or initialize state of last seen tweet IDs
if os.path.exists(config.STATE_FILE):
    with open(config.STATE_FILE, 'r') as f:
        state = json.load(f)
else:
    state = {}

def save_state():
    """Save the current state (last tweet IDs) to disk."""
    with open(config.STATE_FILE, 'w') as f:
        json.dump(state, f)

# Send periodic "I'm alive" messages to admin chat
def send_alive():
    bot.send_message(config.TELEGRAM_ADMIN_CHAT_ID, "Bot is alive and running.")

schedule.every(4).minutes.do(send_alive)

def _send_media_or_text(username, message, photos, videos):
    """
    Helper to send media (photos/videos) or text only.
    Extracted for reuse in eager-post function.
    """
    # Photos
    if photos:
        media_group = []
        for i, url in enumerate(photos):
            filepath = download_media(url)
            if i == 0:
                media = telebot.types.InputMediaPhoto(open(filepath,'rb'),
                                                      caption=message,
                                                      parse_mode='Markdown')
            else:
                media = telebot.types.InputMediaPhoto(open(filepath,'rb'))
            media_group.append(media)
        bot.send_media_group(config.TELEGRAM_CHAT_ID, media_group)
        # cleanup
        for m in media_group:
            try: m.media.close()
            except: pass
        for url in photos:
            fname = os.path.basename(urlparse(url).path)
            fp = os.path.join('downloads', fname)
            if os.path.exists(fp):
                os.remove(fp)

    # Videos
    elif videos:
        vid_path = download_media(videos[0])
        bot.send_video(config.TELEGRAM_CHAT_ID,
                       video=open(vid_path,'rb'),
                       caption=message,
                       parse_mode='Markdown')
        if os.path.exists(vid_path):
            os.remove(vid_path)

    # Text only
    else:
        bot.send_message(config.TELEGRAM_CHAT_ID,
                         message,
                         parse_mode='Markdown')

def post_latest_eager(username: str):
    """
    On startup: fetch exactly the most recent original tweet
    (ignores state) and post it, then record its ID.
    """
    scraper = sntwitter.TwitterUserScraper(username)
    tweet = next(scraper.get_items(), None)
    if not tweet:
        return
    if tweet.inReplyToTweetId or getattr(tweet, 'retweetedTweet', None) or getattr(tweet, 'quotedTweet', None):
        return
    text = tweet.content
    message = format_message(username, text)
    photos, videos = extract_media_urls(tweet)
    _send_media_or_text(username, message, photos, videos)
    state[username] = tweet.id
    save_state()

def process_account(username: str):
    """
    Scrape tweets for a single account and send any new ones.
    Updates state[username] to the newest tweet ID seen.
    """
    last_id = state.get(username)
    scraper = sntwitter.TwitterUserScraper(username)
    new_tweets = []

    if last_id is None:
        # initialize without posting
        for tweet in scraper.get_items():
            state[username] = tweet.id
            save_state()
            return

    for tweet in scraper.get_items():
        if tweet.inReplyToTweetId or getattr(tweet, 'retweetedTweet', None) or getattr(tweet, 'quotedTweet', None):
            continue
        if tweet.id <= last_id:
            break
        new_tweets.append(tweet)

    new_tweets.reverse()
    for tweet in new_tweets:
        text = tweet.content
        message = format_message(username, text)
        photos, videos = extract_media_urls(tweet)
        try:
            _send_media_or_text(username, message, photos, videos)
        except Exception as e:
            print(f"Failed to send tweet {tweet.id} for {username}: {e}")

    if new_tweets:
        state[username] = new_tweets[-1].id
        save_state()

def run():
    """Main loop: first post top-3 immediately, then every 30 seconds."""
    # --- Eager post for first 3 priority accounts ---
    for username in config.ACCOUNTS[:3]:
        try:
            post_latest_eager(username)
        except Exception as e:
            print(f"Eager post failed for {username}: {e}")

    # --- Normal scraping loop ---
    error_count = 0
    while True:
        for username in config.ACCOUNTS:
            try:
                process_account(username)
                error_count = 0
            except Exception as e:
                print(f"Error processing {username}: {e}")
                traceback.print_exc()
                error_count += 1
                if error_count >= 3:
                    bot.send_message(config.TELEGRAM_ADMIN_CHAT_ID,
                                     f"⚠️ Bot encountered repeated errors: {e}")
                    error_count = 0
            schedule.run_pending()
            time.sleep(30)

def start_bot():
    run()
