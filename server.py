from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is alive", 200
