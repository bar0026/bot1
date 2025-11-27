import os
import time
import threading
from flask import Flask, request, jsonify
import telebot
from telebot import types
import logging

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot tokeni (o'zingizniki bilan almashtiring)
BOT_TOKEN = "8346801600:AAGwVSdfvls42KHFtXwbcZhPzBNVEg8rU9g"
bot = telebot.TeleBot(BOT_TOKEN)

# Majburiy obuna kanallari
REQUIRED_CHANNELS = [
    {"name": "1-kanal", "username": "@bsb_chsb_javoblari1"},
    {"name": "2-kanal", "username": "@chsb_original"},
]

# Linklar bazasi
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

# Foydalanuvchilarni saqlash
def save_user(user_id):
    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []
    if str(user_id) not in users:
        users.append(str(user_id))
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(users))

# Obuna tekshirish
def check_subscription_status(user_id):
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(channel["name"])
        except Exception as e:
            not_subscribed.append(channel["name"])
    return not_subscribed

def subscription_buttons(not_subscribed=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    channels = REQUIRED_CHANNELS if not_subscribed is None else [c for c in REQUIRED_CHANNELS if c['name'] in not_subscribed]
    for channel in channels:
        markup.add(types.InlineKeyboardButton(channel['name'], url=f"https://t.me/{channel['username'][1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
    return markup

# Admin panel tugmalari
def admin_panel_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📊 Statistika")
    btn2 = types.KeyboardButton("📣 Xabar yuborish (Hammaga)")
    btn3 = types.KeyboardButton("👤 Foydalanuvchiga xabar")
    btn4 = types.KeyboardButton("🔙 Chiqish")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

# Asosiy menyu
def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📚 BSB JAVOBLARI"),
        types.KeyboardButton("❗️ CHSB JAVOBLARI"),
        types.KeyboardButton("📬 Reklama xizmati")
    )
    return markup

# Sinf tanlash menyusi
def sub_menu_markup(data):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    grades = list(range(5, 12))
    for i in range(0, len(grades), 2):
        row = []
        for grade in grades[i:i+2]:
            txt = f"{grade}-sinf BSB" if data == "bsb" else f"{grade}-sinf CHSB"
            row.append(types.KeyboardButton(txt))
        markup.row(*row)
    markup.add(types.KeyboardButton("🏠 Asosiy menyu"))
    return markup

# Broadcast holati
user_states = {}  # {user_id: {"action": "broadcast_all" | "broadcast_one", "message": message_object}}

# START
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    save_user(user_id)
    welcome = f"""Assalomu alaykum {message.from_user.first_name} 👋🏻
Botimizga xush kelibsiz 🎊
BSB & CHSB javoblari, savollar, slaydlar va esselar — hammasi tekin 🎁

Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling 👇"""
    bot.send_message(message.chat.id, welcome, reply_markup=subscription_buttons())

# Obuna tekshirish
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subscriptions(call):
    not_sub = check_subscription_status(call.from_user.id)
    if not_sub:
        msg = "❌ Quyidagi kanallarga obuna bo‘lmagansiz:\n" + "\n".join(f"• {x}" for x in not_sub)
        markup = subscription_buttons(not_sub)
        bot.answer_callback_query(call.id, "Obuna kerak!", show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "Muvaffaqiyatli!")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="✅ Obuna tasdiqlandi!\nEndi botdan foydalanishingiz mumkin 🎉")
        bot.send_message(call.message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

# Obuna tekshiruvi funksiyasi
def check_user_subscriptions(message_or_call):
    user_id = message_or_call.from_user.id if hasattr(message_or_call, 'from_user') else message_or_call.message.from_user.id
    not_subscribed = check_subscription_status(user_id)
    if not_subscribed:
        msg = "❌ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n" + "\n".join(f"• {name}" for name in not_subscribed)
        bot.send_message(message_or_call.chat.id if hasattr(message_or_call, 'chat') else message_or_call.message.chat.id,
                         msg, reply_markup=subscription_buttons(not_subscribed))
        return False
    return True

# Menyular
@bot.message_handler(func=lambda m: m.text in ["📚 BSB JAVOBLARI", "❗️ CHSB JAVOBLARI", "📬 Reklama xizmati", "🏠 Asosiy menyu"])
def menu_handler(message):
    if not check_user_subscriptions(message): return

    text = message.text
    if text == "📚 BSB JAVOBLARI":
        bot.send_message(message.chat.id, "BSB sinfni tanlang:", reply_markup=sub_menu_markup("bsb"))
    elif text == "❗️ CHSB JAVOBLARI":
        bot.send_message(message.chat.id, "CHSB sinfni tanlang:", reply_markup=sub_menu_markup("chsb"))
    elif text == "📬 Reklama xizmati":
        bot.send_message(message.chat.id, "📬 Reklama uchun: @BAR_xn")
    elif text == "🏠 Asosiy menyu":
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu_markup())

# Sinf tanlash
@bot.message_handler(func=lambda m: any(f"{i}-sinf" in m.text for i in range(5,12)))
def grade_handler(message):
    if not check_user_subscriptions(message): return
    try:
        grade = message.text.split("-")[0]
        typ = "bsb" if "BSB" in message.text else "chsb"
        key = f"{typ}_{grade}"
        link = LINKS.get(key)
        if link:
            bot.send_message(message.chat.id, f"✅ {message.text}\n🔗 Link: {link}\n\nYana tanlash uchun pastdagi tugmalardan foydalaning 👇", reply_markup=main_menu_markup())
        else:
            bot.send_message(message.chat.id, "Bu sinf uchun link topilmadi.")
    except Exception as e:
        logger.error(e)
        bot.send_message(message.chat.id, "Xatolik yuz berdi.")

# ADMIN PANEL
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Siz admin emassiz!")
    bot.send_message(message.chat.id, "🔐 *Admin Panel*ga xush kelibsiz!", parse_mode="Markdown", reply_markup=admin_panel_markup())

@bot.message_handler(func=lambda m: m.text == "🔙 Chiqish" and m.from_user.id == ADMIN_ID)
def admin_exit(message):
    bot.send_message(message.chat.id, "Admin paneldan chiqdingiz.", reply_markup=main_menu_markup())

@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.from_user.id == ADMIN_ID)
def admin_stats(message):
    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            total = len(f.read().splitlines())
    except:
        total = 0
    bot.send_message(message.chat.id, f"📊 Bot foydalanuvchilari soni: *{total}* ta", parse_mode="Markdown")

# Hammaga xabar yuborish
@bot.message_handler(func=lambda m: m.text == "📣 Xabar yuborish (Hammaga)" and m.from_user.id == ADMIN_ID)
def broadcast_all_start(message):
    msg = bot.send_message(message.chat.id, "📩 Hammaga yuboriladigan xabarni yuboring.\nMatn, rasm, video, hujjat bo‘lishi mumkin.\n\n❌ Bekor qilish uchun /cancel yozing.")
    user_states[message.from_user.id] = {"action": "broadcast_all", "msg_id": msg.message_id}

# Bitta foydalanuvchiga xabar
@bot.message_handler(func=lambda m: m.text == "👤 Foydalanuvchiga xabar" and m.from_user.id == ADMIN_ID)
def broadcast_one_start(message):
    bot.send_message(message.chat.id, "Foydalanuvchi ID sini yuboring:\nMasalan: `123456789`", parse_mode="Markdown")
    user_states[message.from_user.id] = {"action": "waiting_id"}

# Bekor qilish
@bot.message_handler(commands=['cancel'])
def cancel_action(message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
        bot.reply_to(message, "❌ Amal bekor qilindi.", reply_markup=admin_panel_markup())

# Xabar qabul qilish va tarqatish
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    state = user_states.get(message.from_user.id)
    if not state:
        return

    if state["action"] == "waiting_id":
        try:
            target_id = int(message.text.strip())
            user_states[message.from_user.id] = {"action": "broadcast_one", "target_id": target_id}
            bot.reply_to(message, f"Endi {target_id} ga yuboriladigan xabarni yuboring:")
        except:
            bot.reply_to(message, "Noto‘g‘ri ID. Faqat raqam yuboring.")
        return

    if state["action"] in ["broadcast_all", "broadcast_one"]:
        target_id = state.get("target_id")
        bot.reply_to(message, "⏳ Xabar yuborilmoqda...")

        def send_message():
            try:
                users = []
                if state["action"] == "broadcast_all":
                    with open("users.txt", "r", encoding="utf-8") as f:
                        users = [int(u) for u in f.read().splitlines() if u.strip()]
                else:
                    users = [target_id]

                success = 0
                failed = 0
                for user_id in users:
                    try:
                        if message.content_type == "text":
                            bot.send_message(user_id, message.text, parse_mode="HTML", disable_web_page_preview=True)
                        elif message.content_type == "photo":
                            bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption, parse_mode="HTML")
                        elif message.content_type == "video":
                            bot.send_video(user_id, message.video.file_id, caption=message.caption)
                        elif message.content_type == "document":
                            bot.send_document(user_id, message.document.file_id, caption=message.caption)
                        elif message.content_type == "animation":
                            bot.send_animation(user_id, message.animation.file_id, caption=message.caption)
                        success += 1
                    except Exception as e:
                        failed += 1
                        if "blocked" in str(e) or "user is deactivated" in str(e):
                            pass  # Bloklaganlarni o‘chirish mumkin (keyinroq)
                    time.sleep(0.05)  # Telegram limitdan qochish uchun

                result = f"✅ Yuborildi: {success}\n❌ Xato: {failed}"
                if state["action"] == "broadcast_one":
                    result = "Xabar muvaffaqiyatli yuborildi!" if success else "Xabar yuborilmadi."
                bot.send_message(message.chat.id, result, reply_markup=admin_panel_markup())
            except Exception as e:
                bot.send_message(message.chat.id, f"Xatolik: {e}")

            if message.from_user.id in user_states:
                del user_states[message.from_user.id]

        threading.Thread(target=send_message, daemon=True).start()

# Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return jsonify({"status": "ok"})

def set_webhook():
    url = f"https://mytelegrammbottest.onrender.com/{BOT_TOKEN}"
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=url)
    logger.info(f"Webhook o'rnatildi: {url}")

def main():
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Server {port}-portda ishga tushdi")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
