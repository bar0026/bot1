import os
import sqlite3
import time
from flask import Flask, request
import telebot
from telebot import types
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
BOT_TOKEN = "8346801600:AAGwVSdfvls42KHFtXwbcZhPzBNVEg8rU9g"  # Tokeningiz
bot = telebot.TeleBot(BOT_TOKEN)
ADMIN_ID = 2051084228

# RENDER DISK UCHUN (agar qo'shgan bo'lsangiz)
DB_PATH = '/opt/render/project/data/users.db' if os.path.exists('/opt/render') else 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, join_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

def add_user(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
                  (user.id, user.username or "", user.first_name or "", now))
        conn.commit()
    except Exception as e:
        logger.error(f"DB xato: {e}")
    finally:
        conn.close()

def get_user_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

# Qolgan qism (obuna, linklar, menyu) — sizning kodingizdek, lekin xatoliklar tuzatildi
REQUIRED_CHANNELS = [
    {"name": "1-kanal", "username": "@bsb_chsb_javoblari1"},
    {"name": "2-kanal", "username": "@chsb_original"},
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

def is_subscribed(user_id):
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["username"], user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            logger.error(f"Obuna tekshirish xatosi: {ch['username']}")
            return False  # Xato bo'lsa, False qaytar (obuna talab qilish uchun)
    return True

def sub_buttons():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in REQUIRED_CHANNELS:
        markup.add(types.InlineKeyboardButton(ch["name"], url=f"https://t.me/{ch['username'][1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
    return markup

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📚 BSB JAVOBLARI", "❗️ CHSB JAVOBLARI")
    markup.add("📬 Reklama xizmati")
    return markup

def grade_menu(typ):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in range(5, 12, 2):
        markup.row(
            types.KeyboardButton(f"{i}-sinf {typ}"),
            types.KeyboardButton(f"{i+1}-sinf {typ}")
        )
    markup.add(types.KeyboardButton("🏠 Asosiy menyu"))
    return markup

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Statistika", "📣 Xabar yuborish")
    markup.add("🔙 Chiqish")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user)
    text = f"""Assalomu alaykum, {message.from_user.first_name}!

BSB va CHSB javoblari – hammasi bir joyda!

Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling 👇"""
    bot.send_message(message.chat.id, text, reply_markup=sub_buttons())

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    bot.answer_callback_query(call.id)
    if is_subscribed(call.from_user.id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!\nMenyudan foydalaning 🎉", 
                              call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "🏠 Asosiy menyu:", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmadingiz! Iltimos, kanallarga qo‘shiling.", show_alert=True)

@bot.message_handler(func=lambda m: m.text in ["📚 BSB JAVOBLARI", "❗️ CHSB JAVOBLARI"])
def select_type(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Obuna bo‘ling! 👇", reply_markup=sub_buttons())
        return
    typ = "BSB" if "BSB" in message.text else "CHSB"
    bot.send_message(message.chat.id, f"📖 {typ} sinfni tanlang:", reply_markup=grade_menu(typ))

@bot.message_handler(func=lambda m: "sinf" in m.text and ("BSB" in m.text or "CHSB" in m.text))
def send_link(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Obuna bo‘ling! 👇", reply_markup=sub_buttons())
        return
    try:
        grade = message.text.split("-")[0].strip()
        typ = "bsb" if "BSB" in message.text else "chsb"
        key = f"{typ}_{grade}"
        link = LINKS.get(key)
        if link:
            bot.send_message(message.chat.id, f"🔗 {message.text}\n\n{link}")
        else:
            bot.send_message(message.chat.id, "❌ Bu sinf uchun link topilmadi.")
    except Exception as e:
        logger.error(f"Link yuborish xatosi: {e}")
        bot.send_message(message.chat.id, "❌ Xatolik yuz berdi. Qayta urinib ko'ring.")

@bot.message_handler(func=lambda m: m.text == "🏠 Asosiy menyu")
def back_main(message):
    bot.send_message(message.chat.id, "🏠 Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📬 Reklama xizmati")
def reklama(message):
    bot.send_message(message.chat.id, "📬 Reklama uchun murojaat: @BAR_xn")

# Admin
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    bot.send_message(message.chat.id, "🔐 Admin panel:", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 Chiqish" and m.from_user.id == ADMIN_ID)
def admin_exit(message):
    bot.send_message(message.chat.id, "🏠 Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["📊 Statistika", "Foydalanuvchilar soni"] and m.from_user.id == ADMIN_ID)
def stats(message):
    count = get_user_count()
    bot.reply_to(message, f"📊 Foydalanuvchilar soni: {count:,} ta")

@bot.message_handler(func=lambda m: m.text == "📣 Xabar yuborish" and m.from_user.id == ADMIN_ID)
def broadcast_start(message):
    msg = bot.send_message(message.chat.id, "✍️ Yuboriladigan xabarni yuboring (matn, rasm, video).\nBekor: /cancel")
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Broadcast bekor qilindi.")
        return
    users = get_all_users()
    total = len(users)
    success = failed = 0
    status_msg = bot.send_message(message.chat.id, f"📤 Yuborilmoqda... 0/{total}")
    for i, user_id in enumerate(users):
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
            success += 1
        except Exception as e:
            logger.error(f"Broadcast xatosi {user_id}: {e}")
            failed += 1
        if (i + 1) % 10 == 0 or i == total - 1:
            bot.edit_message_text(f"📤 {i+1}/{total}\n✅ {success} | ❌ {failed}", message.chat.id, status_msg.message_id)
            time.sleep(0.4)  # Telegram limit
    bot.edit_message_text(f"✅ Tugadi!\nUmumiy: {total} | Yuborildi: {success} | Xato: {failed}", 
                          message.chat.id, status_msg.message_id)

# Webhook
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
        return "Error", 500

@app.route("/")
def index():
    return "Bot ishlayapti! Versiya 2.0"

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(2)
    webhook_url = f"https://mytelegrammbottest.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook o'rnatildi: {webhook_url}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
