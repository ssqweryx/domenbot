import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "7808173982:AAFEBJd3FDT8V-zErqg_EAufaq6FPRad5J0"
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://domenbot.onrender.com{WEBHOOK_PATH}"  # Заменить на свой URL

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-приложение
app = Flask(__name__)

# Создаем Telegram Application
telegram_app = Application.builder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот успешно запущен!")

telegram_app.add_handler(CommandHandler("start", start))

# Синхронный Flask маршрут для Telegram Webhook
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    # Запускаем асинхронную обработку через asyncio.run
    asyncio.run(telegram_app.process_update(update))
    return "ok"

# Тестовый маршрут
@app.route("/")
def index():
    return "Бот работает!"

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )