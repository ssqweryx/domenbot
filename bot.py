import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "твой_токен"
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://domenbot.onrender.com{WEBHOOK_PATH}"  # замените на свой Render URL

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-приложение
app = Flask(__name__)

# Telegram Application
telegram_app = Application.builder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот успешно запущен!")

telegram_app.add_handler(CommandHandler("start", start))

# Flask маршрут для Telegram Webhook
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

# Flask маршрут для теста
@app.route("/")
def index():
    return "Бот работает!"

# Запуск приложения
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=WEBHOOK_URL
    )