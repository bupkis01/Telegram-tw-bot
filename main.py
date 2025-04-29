from threading import Thread
from server import app
from scheduler import start_bot

def run_flask():
    # Launch a dummy HTTP server for health checks
    app.run(host="0.0.0.0", port=8080)

# Start Flask in a background thread
Thread(target=run_flask, daemon=True).start()

# Start the Telegram-scraper bot (blocks here)
start_bot()
