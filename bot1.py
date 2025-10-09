import os
from flask import Flask, request, jsonify
import telebot
from telebot import types
import logging

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = "8346801600:AAGwVSdfvls42KHFtXwbcZhPzBNVEg8rU9g"
bot = telebot.TeleBot(BOT_TOKEN)

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

def save_user(user_id):
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []

    if str(user_id) not in users:
        users.append(str(user_id))
        with open("users.txt", "w") as f:
            f.write("\n".join(users))

def check_subscription_status(user_id):
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except Exception:
            not_subscribed.append(channel["name"])
    return not_subscribed

def main_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("BSB JAVOBLARI ☑️", callback_data="bsb"))
    markup.add(types.InlineKeyboardButton("CHSB JAVOBLARI ❗️", callback_data="chsb"))
    markup.add(types.InlineKeyboardButton("Reklama xizmati 📬", callback_data="reklama"))
    return markup

def subscription_buttons(not_subscribed=None):
    markup = types.InlineKeyboardMarkup()
    channels = REQUIRED_CHANNELS if not_subscribed is None else [c for c in REQUIRED_CHANNELS if c['name'] in not_subscribed]
    for channel in channels:
        markup.add(types.InlineKeyboardButton(channel['name'], url=f"https://t.me/{channel['username'][1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
    return markup

def sub_menu_markup(data):
    markup = types.InlineKeyboardMarkup()
    for grade in range(5, 12):
        if data == "bsb":
            text = f"{grade}-sinf bsb javoblari 📚"
            callback_data = f"bsb_{grade}"
        else:
            text = f"{grade}-sinf chsb javoblari ❇️"
            callback_data = f"chsb_{grade}"
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    markup.add(types.InlineKeyboardButton("🏠 Asosiy menyuga qaytish", callback_data="main_menu"))
    return markup

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    save_user(user_id)

    user_name = message.from_user.first_name
    welcome_text = f"""Assalomu alaykum {user_name} 👋🏻  
Botimizga xush kelibsiz 🎊

Bu bot orqali:
 • Bsb javobi va savoli
 • Chsb javobi va savoli
 • BSB CHSB uchun slayd va esselarni topishingiz mumkin hammasi tekin 🎁  

Botdan foydalanish uchun kanalga obuna boʻling va tekshirish tugmasini bosing ‼️"""

    markup = subscription_buttons()
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subscriptions(call):
    user_id = call.from_user.id
    not_subscribed = check_subscription_status(user_id)

    if not_subscribed:
        msg = "❌ Quyidagi kanallarga obuna bo‘lmagansiz:\n"
        msg += "\n".join(f"• {name}" for name in not_subscribed)
        msg += "\n\nIltimos, quyidagi kanallarga obuna bo‘ling va keyin tekshirib ko‘ring."
        markup = subscription_buttons(not_subscribed)
        bot.answer_callback_query(call.id, "Siz obuna emassiz", show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)
    else:
        msg = "✅ Siz barcha kanallarga obuna bo‘lgansiz!\nEndi botdan foydalanishingiz mumkin 🎉"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)
        # Keyingi menyu
        bot.send_message(chat_id=call.message.chat.id, text="Asosiy menyu:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: call.data in ["bsb", "chsb"])
def sub_menu_handler(call):
    markup = sub_menu_markup(call.data)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.data.upper()} menyusi:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("bsb_") or call.data.startswith("chsb_"))
def grade_selection_handler(call):
    link = LINKS.get(call.data)
    if link:
        text = f"Siz tanladingiz: {call.data.upper()}\nMana siz uchun havola:\n{link}"
    else:
        text = f"Siz tanladingiz: {call.data.upper()}\nKechirasiz, havola topilmadi."
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Asosiy menyu:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: call.data == "reklama")
def reklama_handler(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="📬 Reklama uchun admin bilan bog‘laning: @BAR_xn")

@bot.message_handler(commands=['stats'])
def stats_handler(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Sizda bu buyruqni ishlatishga ruxsat yo'q.")
        return
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []
    bot.send_message(message.chat.id, f"Botni ishlatgan foydalanuvchilar soni: {len(users)}")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return jsonify({"status": "ok"})

def set_webhook():
    webhook_url = f"https://bot1-2jv0.onrender.com/{BOT_TOKEN}"  # O'zingizning URLingiz
    bot.remove_webhook()
    result = bot.set_webhook(url=webhook_url)
    if result:
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.error("Webhook set failed")

def main():
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
