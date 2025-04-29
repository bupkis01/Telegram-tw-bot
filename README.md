# Twitter Scraper Telegram Bot

This bot automatically scrapes tweets from a list of public Twitter accounts and posts them to a Telegram chat. It uses `snscrape` (no Twitter API required) and `pyTelegramBotAPI` to send messages with or without media.

---

## Features

- Scrapes 15 public Twitter accounts in a fixed order.
- Posts only new, original tweets (ignores replies, retweets, quotes).
- Formats each post with a custom display name, tweet content, and a source hashtag.
- Sends tweets with:
  - **Photos** as albums
  - **Videos/GIFs** as Telegram video messages
  - **Text-only** tweets as plain messages
- Keeps track of the last tweet sent using `state.json`.
- Sends a "Bot is alive" message to an admin chat every 4 minutes.
- Sends error alerts to the admin if repeated errors occur.

---

## Requirements

Install required Python packages:

```bash
pip install -r requirements.txt
