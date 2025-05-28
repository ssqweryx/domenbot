import nest_asyncio
nest_asyncio.apply()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import asyncio

user_state = {}

# Меню кнопок
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔟 Сгенерировать 10 ссылок", callback_data="gen_10")],
        [InlineKeyboardButton("3️⃣0️⃣ Сгенерировать 30 ссылок", callback_data="gen_30")],
        [InlineKeyboardButton("5️⃣0️⃣ Сгенерировать 50 ссылок", callback_data="gen_50")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Кнопка "Перезапуск"
def get_restart_menu():
    keyboard = [[InlineKeyboardButton("🔄 Перезапустить", callback_data="restart")]]
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите количество ссылок:", reply_markup=get_main_menu())

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "restart":
        user_state.pop(user_id, None)
        await query.message.reply_text("Бот перезапущен. Выберите количество ссылок:", reply_markup=get_main_menu())
        return

    count = int(query.data.split("_")[1])
    user_state[user_id] = {"count": count}
    await query.message.reply_text("Введите ссылку на NFT-подарок (например: https://t.me/nft/EvilEye-40207)")

# Обработка ссылки
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_state:
        await update.message.reply_text("❗ Сначала выберите количество ссылок через /start")
        return

    base_link = update.message.text.strip()

    try:
        prefix, number_str = base_link.rsplit("-", 1)
        number = int(number_str)
    except:
        await update.message.reply_text("❌ Убедитесь, что ссылка заканчивается на `-число`.")
        return

    count = user_state[user_id]["count"]
    links = [f"<a href='{prefix}-{number + i}'>🎁 Подарок {i + 1}</a>" for i in range(count)]

    await update.message.reply_text(
        "\n".join(links),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_restart_menu()  # Показываем кнопку "Перезапуск"
    )

    user_state.pop(user_id)

# Запуск бота
async def main():
    app = ApplicationBuilder().token("7808173982:AAFEBJd3FDT8V-zErqg_EAufaq6FPRad5J0").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("✅ Бот запущен...")
    await app.run_polling()

asyncio.run(main())