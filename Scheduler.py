# scheduler.py
# Main loop: periodically scrape accounts and send new tweets to Telegram.

import os
import time
import json
import traceback

import schedule
import snscrape.modules.twitter as sntwitter
import telebot

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

# Send periodic "I'm alive" messages to admin chat
def send_alive():
    bot.send_message(config.TELEGRAM_ADMIN_CHAT_ID, "Bot is alive and running.")

schedule.every(4).minutes.do(send_alive)

def save_state():
    """Save the current state (last tweet IDs) to disk."""
    with open(config.STATE_FILE, 'w') as f:
        json.dump(state, f)

def process_account(username: str):
    """
    Scrape tweets for a single account and send any new ones.
    Updates state[username] to the newest tweet ID seen.
    """
    last_id = state.get(username)
    # Scrape user timeline
    scraper = sntwitter.TwitterUserScraper(username)
    new_tweets = []
    if last_id is None:
        # First run for this user: initialize last_id to latest tweet ID
        for tweet in scraper.get_items():
            state[username] = tweet.id
            save_state()
            return  # don't send anything on first run
    # Collect tweets since last_id
    for tweet in scraper.get_items():
        # Skip replies, retweets, and quotes
        if tweet.inReplyToTweetId is not None or getattr(tweet, 'retweetedTweet', None) or getattr(tweet, 'quotedTweet', None):
            continue
        if tweet.id <= last_id:
            break
        new_tweets.append(tweet)
    # Sort tweets chronological (oldest first)
    new_tweets.reverse()
    # Send all new tweets
    for tweet in new_tweets:
        text = tweet.content.replace(tweet.url, "")  # Remove any tweet URL
        message = format_message(username, text)
        photos, videos = extract_media_urls(tweet)
        try:
            # If there are photos, send as media group or single photo
            if photos:
                media_group = []
                for i, photo_url in enumerate(photos):
                    filepath = download_media(photo_url)
                    if i == 0:
                        # First photo: include caption
                        media = telebot.types.InputMediaPhoto(open(filepath, 'rb'), caption=message, parse_mode='Markdown')
                    else:
                        media = telebot.types.InputMediaPhoto(open(filepath, 'rb'))
                    media_group.append(media)
                bot.send_media_group(config.TELEGRAM_CHAT_ID, media_group)
                # Clean up downloaded photos
                for m in media_group:
                    try:
                        m.media.close()
                    except:
                        pass
                for photo_url in photos:
                    fname = os.path.basename(urlparse(photo_url).path)
                    fp = os.path.join('downloads', fname)
                    if os.path.exists(fp):
                        os.remove(fp)
            # Else if there are videos, send the first one
            elif videos:
                vid_path = download_media(videos[0])
                bot.send_video(config.TELEGRAM_CHAT_ID, video=open(vid_path, 'rb'), caption=message, parse_mode='Markdown')
                # Clean up downloaded video
                if os.path.exists(vid_path):
                    os.remove(vid_path)
            else:
                # No media: send text only
                bot.send_message(config.TELEGRAM_CHAT_ID, message, parse_mode='Markdown')
        except Exception as e:
            print(f"Failed to send tweet {tweet.id} for {username}: {e}")
    # Update last_id if we posted any tweets
    if new_tweets:
        state[username] = new_tweets[-1].id
        save_state()

def run():
    """Main loop: iterate accounts on a 30-second schedule."""
    error_count = 0
    while True:
        for username in config.ACCOUNTS:
            try:
                process_account(username)
                # Reset error count on success
                error_count = 0
            except Exception as e:
                print(f"Error processing {username}: {e}")
                traceback.print_exc()
                error_count += 1
                if error_count >= 3:
                    bot.send_message(config.TELEGRAM_ADMIN_CHAT_ID,
                                     f"⚠️ Bot encountered repeated errors: {e}")
                    error_count = 0
            # Run any scheduled jobs (like alive messages)
            schedule.run_pending()
            time.sleep(30)  # Wait 30 seconds before next account

# Entry point for importing
def start_bot():
    run()
