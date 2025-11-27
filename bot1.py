import os
import sqlite3
import threading
import time
from flask import Flask, request, jsonify
import telebot
from telebot import types
import logging
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = "8346801600:AAGwVSdfvls42KHFtXwbcZhPzBNVEg8rU9g"
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 2051084228

# ==================== BAZA ====================
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, join_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

def add_user(user):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
                  (user.id, user.username or "", user.first_name or "", now))
        conn.commit()
    except Exception as e:
        logger.error(f"DB error: {e}")
    finally:
        conn.close()

def get_user_count():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

# ==================== OBUNA TEKSHIRISH ====================
REQUIRED_CHANNELS = [
    {"name": "1-kanal", "username": "@bsb_chsb_javoblari1"},
    {"name": "2-kanal", "username": "@chsb_original"},
]

def is_subscribed(user_id):
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["username"], user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def sub_buttons():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in REQUIRED_CHANNELS:
        markup.add(types.InlineKeyboardButton(ch["name"], url=f"https://t.me/{ch['username'][1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
    return markup

# ==================== MENYULAR ====================
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
    markup.add(types.KeyboardButton("🔙 Asosiy menyu"))
    return markup

LINKS = {
    # BSB
    "bsb_5": "https://www.test-uz.ru/sor_uz.php?klass=5",
    "bsb_6": "https://www.test-uz.ru/sor_uz.php?klass=6",
    "bsb_7": "https://www.test-uz.ru/sor_uz.php?klass=7",
    "bsb_8": "https://www.test-uz.ru/sor_uz.php?klass=8",
    "bsb_9": "https://www.test-uz.ru/sor_uz.php?klass=9",
    "bsb_10": "https://www.test-uz.ru/sor_uz.php?klass=10",
    "bsb_11": "https://www.test-uz.ru/sor_uz.php?klass=11",

    # CHSB
    "chsb_5": "https://www.test-uz.ru/soch_uz.php?klass=5",
    "chsb_6": "https://www.test-uz.ru/soch_uz.php?klass=6",
    "chsb_7": "https://www.test-uz.ru/soch_uz.php?klass=7",
    "chsb_8": "https://www.test-uz.ru/soch_uz.php?klass=8",
    "chsb_9": "https://www.test-uz.ru/soch_uz.php?klass=9",
    "chsb_10": "https://www.test-uz.ru/soch_uz.php?klass=10",
    "chsb_11": "https://www.test-uz.ru/soch_uz.php?klass=11",
}

# ==================== START ====================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user)

    text = f"""Assalomu alaykum, {message.from_user.first_name}! 👋

BSB & CHSB javoblari — hammasi bir joyda! 📚

Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling 👇"""

    bot.send_message(message.chat.id, text, reply_markup=sub_buttons())

# ==================== OBUNANI TEKSHIRISH ====================
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    if is_subscribed(call.from_user.id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!\n\nMenyudan foydalaning 👇",
                              call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "📌 Bosh menyu:", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❗️ Hali obuna bo‘lmagansiz!", show_alert=True)

# ==================== BSB / CHSB TANLASH ====================
@bot.message_handler(func=lambda m: m.text in ["📚 BSB JAVOBLARI", "❗️ CHSB JAVOBLARI"])
def select_type(message):
    if not is_subscribed(message.from_user.id):
        return bot.send_message(message.chat.id, "❗️ Iltimos, avval obuna bo‘ling", reply_markup=sub_buttons())

    typ = "BSB" if "BSB" in message.text else "CHSB"
    bot.send_message(message.chat.id, f"{typ} sinfni tanlang:", reply_markup=grade_menu(typ))

# ==================== LINK YUBORISH ====================
@bot.message_handler(func=lambda m: "sinf" in m.text)
def get_link(message):
    try:
        grade = message.text.split("-")[0]
        typ = "bsb" if "BSB" in message.text else "chsb"
        key = f"{typ}_{grade}"

        link = LINKS.get(key)
        if link:
            bot.send_message(message.chat.id, f"📘 *{message.text}*\n\n🔗 Link: {link}", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❗️ Bu sinf uchun link mavjud emas.")
    except:
        bot.send_message(message.chat.id, "❗️ Xatolik yuz berdi.")

# ==================== REKLAMA ====================
@bot.message_handler(func=lambda m: m.text == "📬 Reklama xizmati")
def reklama(message):
    bot.send_message(message.chat.id, "📢 Reklama uchun: @BAR_xn")

# ==================== ADMIN PANEL ====================
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Statistika", "📣 Xabar yuborish")
    markup.add("👥 Foydalanuvchilar soni", "🔙 Chiqish")
    return markup

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Ruxsat yo‘q!")
    bot.send_message(message.chat.id, "🔐 *Admin panelga xush kelibsiz!*",
                     reply_markup=admin_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 Chiqish" and m.from_user.id == ADMIN_ID)
def admin_exit(message):
    bot.send_message(message.chat.id, "🏠 Asosiy menyu", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["📊 Statistika", "👥 Foydalanuvchilar soni"] and m.from_user.id == ADMIN_ID)
def stats(message):
    count = get_user_count()
    bot.reply_to(message, f"📊 Foydalanuvchilar: *{count}* ta", parse_mode="Markdown")

# ==================== BROADCAST ====================
@bot.message_handler(func=lambda m: m.text == "📣 Xabar yuborish" and m.from_user.id == ADMIN_ID)
def broadcast_start(message):
    msg = bot.send_message(message.chat.id, "📨 Yubormoqchi bo‘lgan xabarni yuboring.\n\n❌ Bekor qilish: /cancel")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(message):
    if message.text == "/cancel":
        return bot.send_message(message.chat.id, "❌ Bekor qilindi.")

    users = get_all_users()
    total = len(users)
    success = failed = 0

    status = bot.send_message(message.chat.id, f"📤 Yuborilmoqda... 0/{total}")

    for i, user_id in enumerate(users):
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
            success += 1
        except:
            failed += 1

        if (i + 1) % 10 == 0 or i == total - 1:
            bot.edit_message_text(f"📤 Yuborilmoqda...\n"
                                  f"✔️ {success}\n❌ {failed}\nUmumiy: {total}",
                                  message.chat.id, status.message_id)

    bot.edit_message_text(
        f"✅ *Broadcast tugadi!*\n\n"
        f"✔️ Yuborildi: {success}\n❌ Xato: {failed}\n📊 Umumiy: {total}",
        message.chat.id, status.message_id, parse_mode="Markdown"
    )

# ==================== WEBHOOK ====================
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot ishlamoqda!"

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://mytelegrammbottest.onrender.com/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
