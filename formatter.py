# formatter.py
# Functions to format the Telegram message for a tweet.

import config

def format_message(username: str, tweet_text: str) -> str:
    """
    Format the tweet into the Telegram message format:
      **DisplayName🚨**
      Tweet text
      🔗Source #Hashtag
    Uses mappings from config.HEADLINE_NAME and config.SOURCE_HASHTAG.
    """
    # Get the custom display name; default to username if not found
    display_name = config.HEADLINE_NAME.get(username, username)
    # Emoji tag is appended to the display name
    header = f"**{display_name}🚨**"
    # Append the tweet content (preserve newlines and emojis)
    body = tweet_text.strip()
    # Get the hashtag for the source; default to display name if not set
    hashtag = config.SOURCE_HASHTAG.get(username, "")
    footer = f"🔗Source {hashtag}" if hashtag else "🔗Source"
    # Combine all parts
    return f"{header}\n{body}\n{footer}"
