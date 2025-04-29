# main.py
# Entry point: launches both the dummy Flask server (for health checks)
# and the Twitter-scraper Telegram bot.

from threading import Thread
from server import app
from scheduler import start_bot

def run_flask():
    """
    Dummy HTTP server so platforms like Koyeb and UptimeRobot
    can ping a /health endpoint and keep the service alive.
    """
    app.run(host="0.0.0.0", port=8080)

# Start the Flask server in a daemon thread (will not block shutdown)
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

# Start the main bot loop (this will block and run indefinitely)
start_bot()
