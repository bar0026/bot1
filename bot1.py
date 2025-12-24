# bot1.py – polling (webhook-siz)
import os
import sqlite3
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("TOKEN")      # env dan o‘qiydi
bot = telebot.TeleBot(BOT_TOKEN)
ADMIN_ID = 2051084228

# ---------- DATABASE ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                msg_count INTEGER DEFAULT 0
            )
        """)

def save_user(user_id, first_name="NoName"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO users(user_id, first_name, msg_count) VALUES(?,?,0)",
                     (user_id, first_name))

def increase_msg_count(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET msg_count = msg_count + 1 WHERE user_id = ?", (user_id,))

def get_all_users():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT user_id, first_name, msg_count FROM users").fetchall()

# ---------- CONSTANTS ----------
REQUIRED_CHANNELS = [
    {"name": "1-kanal", "username": "@bsb_chsb_javoblari1"},
    {"name": "2-kanal", "username": "@chsb_original"},
    {"name": "3-kanal", "username": "@kulishamiz_keling"},
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

# ---------- UTILS ----------
def check_subscription_status(user_id):
    not_sub = []
    for ch in REQUIRED_CHANNELS:
        try:
            status = bot.get_chat_member(chat_id=ch["username"], user_id=user_id).status
            if status not in ("member", "administrator", "creator"):
                not_sub.append(ch["name"])
        except Exception:
            not_sub.append(ch["name"])
    return not_sub

def subscription_buttons(not_sub=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    channels = REQUIRED_CHANNELS if not_sub is None else [c for c in REQUIRED_CHANNELS if c["name"] in not_sub]
    for c in channels:
        markup.add(types.InlineKeyboardButton(c["name"], url=f"https://t.me/{c['username'][1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
    return markup

def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📚 BSB JAVOBLARI"),
        types.KeyboardButton("❗️ CHSB JAVOBLARI"),
        types.KeyboardButton("📬 Reklama xizmati")
    )
    return markup

def sub_menu_markup(typ):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in range(5, 12, 2):
        row = []
        for g in range(i, min(i + 2, 12)):
            txt = f"{g}-sinf BSB" if typ == "bsb" else f"{g}-sinf CHSB"
            row.append(types.KeyboardButton(txt))
        markup.row(*row)
    markup.add(types.KeyboardButton("🏠 Asosiy menyu"))
    return markup

# ---------- HANDLERS ----------
@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    save_user(uid, message.from_user.first_name)
    increase_msg_count(uid)
    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum {message.from_user.first_name} 👋🏻\nBotimizga xush kelibsiz 🎊",
        reply_markup=subscription_buttons()
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_subs")
def check_subscriptions(call):
    uid = call.from_user.id
    save_user(uid, call.from_user.first_name)
    increase_msg_count(uid)
    not_sub = check_subscription_status(uid)
    if not_sub:
        msg = "❌ Quyidagi kanallarga obuna emassiz:\n" + "\n".join(f"• {x}" for x in not_sub)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                              reply_markup=subscription_buttons(not_sub))
        bot.answer_callback_query(call.id, "Obuna kerak!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "Tasdiqlandi!")
        bot.edit_message_text("✅ Obuna tasdiqlandi!", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

@bot.message_handler(func=lambda m: m.text in ["📚 BSB JAVOBLARI", "❗️ CHSB JAVOBLARI", "📬 Reklama xizmati", "🏠 Asosiy menyu"])
def menu_handler(message):
    uid = message.from_user.id
    save_user(uid, message.from_user.first_name)
    increase_msg_count(uid)
    if message.text == "📚 BSB JAVOBLARI":
        bot.send_message(message.chat.id, "BSB sinfni tanlang:", reply_markup=sub_menu_markup("bsb"))
    elif message.text == "❗️ CHSB JAVOBLARI":
        bot.send_message(message.chat.id, "CHSB sinfni tanlang:", reply_markup=sub_menu_markup("chsb"))
    elif message.text == "📬 Reklama xizmati":
        bot.send_message(message.chat.id, "📬 Reklama uchun: @BAR_xn")
    elif message.text == "🏠 Asosiy menyu":
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

@bot.message_handler(func=lambda m: any(f"{i}-sinf" in m.text for i in range(5, 12)))
def grade_handler(message):
    uid = message.from_user.id
    save_user(uid, message.from_user.first_name)
    increase_msg_count(uid)
    try:
        grade = message.text.split("-")[0]
        typ = "bsb" if "BSB" in message.text else "chsb"
        link = LINKS.get(f"{typ}_{grade}")
        if link:
            bot.send_message(message.chat.id, f"🔗 {message.text}\nLink: {link}", reply_markup=main_menu_markup())
        else:
            bot.send_message(message.chat.id, "Bu sinf uchun link topilmadi.")
    except Exception:
        bot.send_message(message.chat.id, "Xatolik yuz berdi.")

# ---------------- ADMIN ----------------
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ Siz admin emassiz!")
    save_user(message.from_user.id, message.from_user.first_name)
    increase_msg_count(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📊 Statistika"),
        types.KeyboardButton("📣 Xabar yuborish (Hammaga)"),
        types.KeyboardButton("👤 Foydalanuvchiga xabar"),
        types.KeyboardButton("🔙 Chiqish")
    )
    bot.send_message(message.chat.id, "🔐 Admin panel", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔙 Chiqish" and m.from_user.id == ADMIN_ID)
def admin_exit(message):
    bot.send_message(message.chat.id, "Admin paneldan chiqdingiz.", reply_markup=main_menu_markup())

@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.from_user.id == ADMIN_ID)
def admin_stats(message):
    users = get_all_users()
    total = len(users)
    top = sorted(users, key=lambda x: x[2], reverse=True)[:10]
    top_txt = "\n".join([f"{i+1}. {u[1]} — {u[2]} ta xabar" for i, u in enumerate(top)]) or "Ma'lumot yo‘q"
    bot.send_message(message.chat.id, f"📊 Foydalanuvchilar soni: {total} ta\n\n🔥 Eng faol:\n{top_txt}")

USER_STATES = {}

@bot.message_handler(func=lambda m: m.text == "📣 Xabar yuborish (Hammaga)" and m.from_user.id == ADMIN_ID)
def broadcast_all_start(message):
    bot.send_message(message.chat.id, "📩 Hammaga yuboriladigan xabarni yuboring.")
    USER_STATES[message.from_user.id] = "broadcast_all"

@bot.message_handler(func=lambda m: m.text == "👤 Foydalanuvchiga xabar" and m.from_user.id == ADMIN_ID)
def broadcast_one_start(message):
    bot.send_message(message.chat.id, "Foydalanuvchi ID sini yuboring:")
    USER_STATES[message.from_user.id] = "waiting_id"

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'animation'])
def handle_broadcast(message):
    uid = message.from_user.id
    if uid != ADMIN_ID or uid not in USER_STATES:
        return
    state = USER_STATES[uid]
    if state == "waiting_id":
        try:
            target = int(message.text)
            USER_STATES[uid] = ("broadcast_one", target)
            bot.send_message(uid, "Endi yuboriladigan xabarni yuboring:")
        except ValueError:
            bot.send_message(uid, "Noto‘g‘ri ID. Raqam yozing.")
        return

    if state == "broadcast_all":
        users_list = [u[0] for u in get_all_users()]
    else:
        users_list = [state[1]]

    ok = 0
    for usr in users_list:
        try:
            if message.content_type == "text":
                bot.send_message(usr, message.text)
            elif message.content_type == "photo":
                bot.send_photo(usr, message.photo[-1].file_id, caption=message.caption)
            ok += 1
        except Exception:
            pass
    bot.send_message(uid, f"Yuborildi: {ok} ta")
    USER_STATES.pop(uid, None)

# ---------- POLLING START ----------
if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=20)
