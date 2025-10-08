import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import logging

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask ilovasini yaratamiz
app = Flask(__name__)

# Telegram bot tokeni
BOT_TOKEN = "8346801600:AAGwVSdfvls42KHFtXwbcZhPzBNVEg8rU9g"

# Telegram bot ilovasini yaratamiz
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# REQUIRED_CHANNELS va LINKS ro'yxatlari (o'zgarmagan)
REQUIRED_CHANNELS = [
    {"name": "1-kanal", "username": "@bsb_chsb_javoblari1"},
    {"name": "2-kanal", "username": "@Matematika_6sinf_yechimi_2022"},
    {"name": "3-kanal", "username": "@algebra_7_sinf_yechimi_2022"},
]

LINKS = {
    "bsb_5": "https://www.test-uz.ru/sor_uz.php?klass=5",
    "bsb_6": "https://www.test-uz.ru/sor_uz.php?klass=6",
    "bsb_7": "https://www.test-uz.ru/sor_uz.php?klass=7",
    "bsb_8": "https://www.test-uz.ru/sor_uz.php?klass=8",
    "bsb_9": "https://www.test-uz.ru/sor_uz.php?klass=9",
    "bsb_10": "https://www.test-uz.ru/sor_uz.php?klass=10",
    "bsb_11": "https://www.test-uz.ru/sor_uz.php?klass=11",
    "chsb_5": "https://www.test-uz.ru/soch_uz.php?klass=5",
    "chsb_6": "https://www.test-uz.ru/soch_uz.php?klass=6",
    "chsb_7": "https://www.test-uz.ru/soch_uz.php?klass=7",
    "chsb_8": "https://www.test-uz.ru/soch_uz.php?klass=8",
    "chsb_9": "https://www.test-uz.ru/soch_uz.php?klass=9",
    "chsb_10": "https://www.test-uz.ru/soch_uz.php?klass=10",
    "chsb_11": "https://www.test-uz.ru/soch_uz.php?klass=11",
}

ADMIN_ID = 2051084228

# Obuna holatini tekshirish
async def check_subscription_status(context, user_id):
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except Exception:
            not_subscribed.append(channel["name"])
    return not_subscribed

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Foydalanuvchini users.txt faylga yozamiz
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []

    if str(user_id) not in users:
        users.append(str(user_id))
        with open("users.txt", "w") as f:
            f.write("\n".join(users))

    user = update.effective_user.first_name
    welcome_text = f"""Assalomu alaykum {user} 👋🏻  
Botimizga xush kelibsiz 🎊

Bu bot orqali:
 • Bsb javobi va savoli
 • Chsb javobi va savoli
 • BSB CHSB uchun slayd va esselarni topishingiz mumkin hammasi tekin 🎁  

Botdan foydalanish uchun kanalga obuna boʻling va tekshirish tugmasini bosing ‼️"""

    subscribe_buttons = [
        [InlineKeyboardButton(channel['name'], url=f"https://t.me/{channel['username'][1:]}")]
        for channel in REQUIRED_CHANNELS
    ]
    subscribe_buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")])

    reply_markup = InlineKeyboardMarkup(subscribe_buttons)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Obuna tekshiruvi
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    not_subscribed = await check_subscription_status(context, user_id)

    if not_subscribed:
        msg = "❌ Quyidagi kanallarga obuna bo‘lmagansiz:\n"
        msg += "\n".join(f"• {name}" for name in not_subscribed)
        msg += "\n\nIltimos, quyidagi kanallarga obuna bo‘ling va keyin tekshirib ko‘ring."

        subscribe_buttons = [
            [InlineKeyboardButton(channel['name'], url=f"https://t.me/{channel['username'][1:]}")]
            for channel in REQUIRED_CHANNELS if channel['name'] in not_subscribed
        ]
        subscribe_buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")])
        reply_markup = InlineKeyboardMarkup(subscribe_buttons)

        await query.answer(text="Siz obuna emassiz", show_alert=True)
        await query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        msg = "✅ Siz barcha kanallarga obuna bo‘lgansiz!\nEndi botdan foydalanishingiz mumkin 🎉"
        await query.answer()
        await query.edit_message_text(msg)
        await send_main_menu(query, context)

# Asosiy menyu
async def send_main_menu(update_or_query, context):
    buttons = [
        [InlineKeyboardButton("BSB JAVOBLARI ☑️", callback_data="bsb")],
        [InlineKeyboardButton("CHSB JAVOBLARI ❗️", callback_data="chsb")],
        [InlineKeyboardButton("Reklama xizmati 📬", callback_data="reklama")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text("Asosiy menyu:", reply_markup=markup)
    else:
        await update_or_query.edit_message_text("Asosiy menyu:", reply_markup=markup)

# Sub-menyu (BSB yoki CHSB)
async def send_sub_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    buttons = []
    for grade in range(5, 12):
        if data == "bsb":
            text = f"{grade}-sinf bsb javoblari 📚"
            callback_data = f"bsb_{grade}"
        else:
            text = f"{grade}-sinf chsb javoblari ❇️"
            callback_data = f"chsb_{grade}"
        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton("🏠 Asosiy menyuga qaytish", callback_data="main_menu")])

    markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(f"{data.upper()} menyusi:", reply_markup=markup)

# Sinf tanlash
async def handle_grade_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    link = LINKS.get(data)

    if link:
        await query.answer()
        await query.edit_message_text(
            f"Siz tanladingiz: {data.upper()}\nMana siz uchun havola:\n{link}"
        )
    else:
        await query.answer()
        await query.edit_message_text(
            f"Siz tanladingiz: {data.upper()}\nKechirasiz, havola topilmadi."
        )

# Asosiy menyuga qaytish
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await send_main_menu(query, context)

# Reklama xizmati
async def reklama_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📬 Reklama uchun admin bilan bog‘laning: @BAR_xn")

# Statistika
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sizda bu buyruqni ishlatishga ruxsat yo'q.")
        return

    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []

    await update.message.reply_text(f"Botni ishlatgan foydalanuvchilar soni: {len(users)}")

# Handlerlarni qo'shish
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("stats", stats))
telegram_app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subs"))
telegram_app.add_handler(CallbackQueryHandler(send_sub_menu, pattern="^(bsb|chsb)$"))
telegram_app.add_handler(CallbackQueryHandler(handle_grade_selection, pattern="^(bsb|chsb)_[5-9]|(bsb|chsb)_1[0-1]$"))
telegram_app.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
telegram_app.add_handler(CallbackQueryHandler(reklama_handler, pattern="reklama"))

# Flask webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    if update:
        await telegram_app.process_update(update)
    return jsonify({"status": "ok"})

# Webhookni sozlash
async def set_webhook():
    webhook_url = f"https://bot1-2jv0.onrender.com/{BOT_TOKEN}"  # Render URLingizni kiriting
    await telegram_app.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# Flask serverni ishga tushirish
def main():
    # Initialize the application
    asyncio.run(telegram_app.initialize())
    
    # Webhookni o'rnatamiz
    asyncio.run(set_webhook())
    
    # Flask serverni ishga tushiramiz
    port = int(os.environ.get("PORT", 5000))  # Render PORT o'zgaruvchisini oladi
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
