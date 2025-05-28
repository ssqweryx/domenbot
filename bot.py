from flask import Flask, request
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "YOUR_TOKEN_HERE"
WEBHOOK_PATH = f"/webhook/{TOKEN.split(':')[0]}"
WEBHOOK_URL = f"https://your.domain.com{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

def get_keyboard():
    keyboard = [
        [InlineKeyboardButton("Кнопка 1", callback_data="1")],
        [InlineKeyboardButton("Перезапустить", callback_data="restart")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command from {update.effective_user.id}")
    await update.message.reply_text("Выберите кнопку", reply_markup=get_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "restart":
        await query.message.reply_text("Бот перезапущен. Выберите кнопку:", reply_markup=get_keyboard())
    else:
        await query.message.reply_text(f"Вы нажали кнопку {query.data}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Бот работает!"

if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "8443")),
        webhook_url=WEBHOOK_URL,
    )
