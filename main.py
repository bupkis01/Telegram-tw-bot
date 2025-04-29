from threading import Thread
from server import app

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()
