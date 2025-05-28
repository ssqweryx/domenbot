import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "твой_токен"
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://domenbot.onrender.com{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот успешно запущен!")

telegram_app.add_handler(CommandHandler("start", start))

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Бот работает!"

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    # Запускаем telegram_app, чтобы подготовить его (но не run_webhook!)
    asyncio.run(telegram_app.initialize())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)