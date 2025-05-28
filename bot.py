import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

TOKEN = "7808173982:AAFEBJd3FDT8V-zErqg_EAufaq6FPRad5J0"
WEBHOOK_PATH = f"/webhook/{TOKEN.split(':')[0]}"
WEBHOOK_URL = f"https://domenbot.onrender.com{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

CHOOSING_AMOUNT, WAITING_LINK = range(2)
user_data = {}

def get_amount_keyboard():
    keyboard = [
        [InlineKeyboardButton("Сгенерировать 30 ссылок", callback_data="30")],
        [InlineKeyboardButton("Сгенерировать 50 ссылок", callback_data="50")],
        [InlineKeyboardButton("Сгенерировать 100 ссылок", callback_data="100")],
        [InlineKeyboardButton("Перезапустить бота", callback_data="restart")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выбери, сколько ссылок сгенерировать:",
        reply_markup=get_amount_keyboard()
    )
    return CHOOSING_AMOUNT

async def choose_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "restart":
        user_data.pop(query.message.chat_id, None)
        await query.message.reply_text(
            "Бот перезапущен. Выбери количество ссылок:",
            reply_markup=get_amount_keyboard()
        )
        return CHOOSING_AMOUNT

    amount = int(query.data)
    user_data[query.message.chat_id] = amount
    await query.message.reply_text("Отправь пример ссылки на NFT подарок")
    return WAITING_LINK

def generate_links(base_link: str, count: int):
    import re
    match = re.search(r'(\d+)$', base_link)
    if not match:
        base = base_link.rstrip('/')
        return [f"{base}/{i+1}" for i in range(count)]
    else:
        start_index = match.start(1)
        prefix = base_link[:start_index]
        return [f"{prefix}{i+1}" for i in range(count)]

async def received_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    amount = user_data.get(chat_id)

    if not amount:
        await update.message.reply_text("Пожалуйста, сначала выбери количество ссылок командой /start")
        return ConversationHandler.END

    base_link = update.message.text.strip()
    links = generate_links(base_link, amount)

    chunk_size = 10
    for i in range(0, len(links), chunk_size):
        chunk = links[i:i+chunk_size]
        await update.message.reply_text("\n".join(chunk))

    await update.message.reply_text(
        "Если хочешь перезапустить бота, нажми кнопку ниже:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Перезапустить бота", callback_data="restart")]]
        )
    )

    user_data.pop(chat_id, None)
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, используй кнопки или команду /start для начала.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING_AMOUNT: [CallbackQueryHandler(choose_amount)],
        WAITING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_link)],
    },
    fallbacks=[CommandHandler('start', start)],
    allow_reentry=True,
)

telegram_app.add_handler(conv_handler)
telegram_app.add_handler(MessageHandler(filters.COMMAND, unknown))
telegram_app.add_error_handler(error_handler)

@app.route("/")
def index():
    return "Бот работает!"

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    logging.info("Webhook received")
    data = await request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL,
    )