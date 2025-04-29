# config.py
# Load configuration, mappings, and environment variables.

import os
import json
from dotenv import load_dotenv

# Load environment variables from environment.env
load_dotenv()  # Requires 'python-dotenv' package

# Telegram bot token and chat IDs (set these in environment.env)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Your bot token, e.g., 123456:ABC-DEF...
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')      # ID or username of the target chat for tweets
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')  # ID of your private admin chat for alerts

# Load account list and sort by priority
try:
    with open('name_priority.json', 'r') as f:
        name_priority = json.load(f)
except FileNotFoundError:
    name_priority = []
# Expect name_priority.json as a list of {"username": "...", "priority": n}
# Sort accounts by numeric priority (ascending)
name_priority_sorted = sorted(name_priority, key=lambda x: x.get("priority", 0))
# Extract only the usernames in sorted order
ACCOUNTS = [entry["username"] for entry in name_priority_sorted]

# Load display names mapping
try:
    with open('headline_name.json', 'r') as f:
        HEADLINE_NAME = json.load(f)  # e.g. {"elonmusk": "Elon Musk", ...}
except FileNotFoundError:
    HEADLINE_NAME = {}

# Load source hashtag mapping
try:
    with open('source_hashtag.json', 'r') as f:
        SOURCE_HASHTAG = json.load(f)  # e.g. {"elonmusk": "#SpaceX", ...}
except FileNotFoundError:
    SOURCE_HASHTAG = {}

# State file for last posted tweet IDs
STATE_FILE = 'state.json'
