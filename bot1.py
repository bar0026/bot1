import os
from flask import Flask, request, jsonify
import telebot
from telebot import types
import logging

# Logging sozlamalar
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = "8346801600:AAGwVSdfvls42KHFtXwbcZhPzBNVEg8rU9g"
bot = telebot.TeleBot(BOT_TOKEN)

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

ADMIN_ID = 2051084228

# ------------------------------ FOYDALANUVCHI BAZASI ------------------------------
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

# ------------------------------ OBUNA TEKSHIRISH ------------------------------
def check_subscription_status(user_id):
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except:
            not_subscribed.append(channel["name"])
    return not_subscribed

def subscription_buttons(not_subscribed=None):
    markup = types.InlineKeyboardMarkup()
    channels = REQUIRED_CHANNELS if not_subscribed is None else [c for c in REQUIRED_CHANNELS if c['name'] in not_subscribed]
    for channel in channels:
        markup.add(types.InlineKeyboardButton(channel['name'], url=f"https://t.me/{channel['username'][1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
    return markup

def check_user_subscriptions(message_or_call):
    user_id = message_or_call.from_user.id
    chat_id = message_or_call.message.chat.id if hasattr(message_or_call, "message") else message_or_call.chat.id

    not_subscribed = check_subscription_status(user_id)
    if not_subscribed:
        msg = "❌ Siz quyidagi kanallarga obuna bo‘lmagansiz:\n"
        msg += "\n".join(f"• {name}" for name in not_subscribed)
        msg += "\n\nIltimos, obuna bo‘ling va qayta tekshiring."
        markup = subscription_buttons(not_subscribed)

        if hasattr(message_or_call, "message"):
            bot.answer_callback_query(message_or_call.id, "Obuna shart!", show_alert=True)
            bot.edit_message_text(chat_id=chat_id, message_id=message_or_call.message.message_id,
                                  text=msg, reply_markup=markup)
        else:
            bot.send_message(chat_id, msg, reply_markup=markup)
        return False
    return True

# ------------------------------ MENYU TUGMALARI ------------------------------
def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📚 BSB JAVOBLARI"),
        types.KeyboardButton("❗️ CHSB JAVOBLARI"),
        types.KeyboardButton("📬 Reklama xizmati")
    )
    return markup

def sub_menu_markup(data):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    grades = list(range(5, 12))
    for i in range(0, len(grades), 2):
        row = []
        for grade in grades[i:i + 2]:
            txt = f"{grade}-sinf BSB" if data == "bsb" else f"{grade}-sinf CHSB"
            row.append(types.KeyboardButton(txt))
        markup.row(*row)
    markup.add(types.KeyboardButton("🏠 Asosiy menyu"))
    return markup

# ------------------------------ START ------------------------------
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    save_user(user_id)

    welcome = f"""Assalomu alaykum {message.from_user.first_name} 👋🏻  
Botimizga xush kelibsiz 🎊

BSB & CHSB javoblari, savollar, slaydlar va esselar — hammasi tekin 🎁

Botdan foydalanish uchun kanallarga obuna bo‘ling 👇
"""
    bot.send_message(message.chat.id, welcome, reply_markup=subscription_buttons())

# ------------------------------ OBUNANI TEKSHIRISH ------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subscriptions(call):
    user_id = call.from_user.id
    not_sub = check_subscription_status(user_id)

    if not_sub:
        msg = "❌ Quyidagi kanallarga obuna bo‘lmagansiz:\n" + "\n".join(f"• {x}" for x in not_sub)
        markup = subscription_buttons(not_sub)
        bot.answer_callback_query(call.id, "Obuna kerak", show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="✅ Obuna tasdiqlandi!\nMenyudan foydalanishingiz mumkin 🎉")
        bot.send_message(call.message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

# ------------------------------ BSB / CHSB ------------------------------
@bot.message_handler(func=lambda m: m.text == "📚 BSB JAVOBLARI")
def bsb_menu(message):
    if not check_user_subscriptions(message): return
    bot.send_message(message.chat.id, "BSB sinfni tanlang:", reply_markup=sub_menu_markup("bsb"))

@bot.message_handler(func=lambda m: m.text == "❗️ CHSB JAVOBLARI")
def chsb_menu(message):
    if not check_user_subscriptions(message): return
    bot.send_message(message.chat.id, "CHSB sinfni tanlang:", reply_markup=sub_menu_markup("chsb"))

@bot.message_handler(func=lambda m: m.text == "📬 Reklama xizmati")
def reklama_menu(message):
    if not check_user_subscriptions(message): return
    bot.send_message(message.chat.id, "📬 Reklama uchun: @BAR_xn")

@bot.message_handler(func=lambda m: m.text == "🏠 Asosiy menyu")
def back_to_menu(message):
    bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

# ------------------------------ Sinf linklari ------------------------------
@bot.message_handler(func=lambda m: any(x in m.text for x in ["BSB", "CHSB"]))
def grade_handler(message):
    if not check_user_subscriptions(message): return

    try:
        grade = message.text.split()[0].replace("-sinf", "")
        typ = "bsb" if "BSB" in message.text else "chsb"
        key = f"{typ}_{grade}"
        link = LINKS.get(key)

        if link:
            bot.send_message(message.chat.id, f"Siz tanladingiz: {message.text}\n🔗 Link: {link}")
        else:
            bot.send_message(message.chat.id, "Bu sinf uchun link topilmadi.")
    except Exception as e:
        logger.error(e)
        bot.send_message(message.chat.id, "Xatolik yuz berdi.")

# ------------------------------ ADMIN PANEL ------------------------------
def admin_panel_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📣 Xabar yuborish"),
        types.KeyboardButton("📊 Statistika")
    )
    markup.add(types.KeyboardButton("🔙 Orqaga"))
    return markup

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ Siz admin emassiz.")
    bot.send_message(message.chat.id, "🔐 Admin panel:", reply_markup=admin_panel_markup())

@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def back_to_main(message):
    bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def admin_stats(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
    except:
        users = []
    bot.send_message(message.chat.id, f"📊 Foydalanuvchilar soni: {len(users)}")

# ------------------------------ BROADCAST ------------------------------
broadcast_mode = {}

@bot.message_handler(func=lambda m: m.text == "📣 Xabar yuborish")
def start_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    broadcast_mode[message.from_user.id] = True
    bot.send_message(message.chat.id, "✍️ Yuboriladigan xabarni kiriting.\nMatn, rasm yoki video bo‘lishi mumkin.")

@bot.message_handler(content_types=["text", "photo", "video"])
def broadcast(message):
    if message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id]:

        try:
            with open("users.txt", "r") as f:
                users = f.read().splitlines()
        except:
            users = []

        bot.send_message(message.chat.id, "📤 Yuborilmoqda...")

        ok, fail = 0, 0

        for user in users:
            try:
                if message.content_type == "text":
                    bot.send_message(user, message.text)
                elif message.content_type == "photo":
                    bot.send_photo(user, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == "video":
                    bot.send_video(user, message.video.file_id, caption=message.caption)
                ok += 1
            except:
                fail += 1

        bot.send_message(message.chat.id, f"📣 Yuborildi!\n✔️ {ok} ta\n❌ {fail} ta")
        broadcast_mode[message.from_user.id] = False

# ------------------------------ WEBHOOK ------------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return jsonify({"ok": True})

def set_webhook():
    url = f"https://mytelegrammbottest.onrender.com/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=url)
    logger.info(f"Webhook o‘rnatildi: {url}")

def main():
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Server {port}-portda ishga tushdi")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

