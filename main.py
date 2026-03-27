import telebot
from instagrapi import Client
import threading
import time

# --- بياناتك ---
TOKEN = '8607922156:AAFHV0f9aHoNH0aQcusL_4oo0NFIhH_B9Ds'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = 486391606

bot = telebot.TeleBot(TOKEN)
cl = Client()

seen_messages = set()

# تسجيل دخول انستغرام
def login():
    try:
        cl.login(INSTA_USER, INSTA_PASS)
        print("✅ تم تسجيل الدخول لانستغرام")
        return True
    except Exception as e:
        print("❌ خطأ تسجيل الدخول:", e)
        return False

# مراقبة الدايركت
def monitor_dm():
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                for msg in thread.messages:
                    if msg.id not in seen_messages:
                        seen_messages.add(msg.id)

                        if msg.text:
                            bot.send_message(MY_CHAT_ID, f"📩 {msg.text}")

                        if msg.video_url:
                            bot.send_video(MY_CHAT_ID, msg.video_url)

                        if msg.photo:
                            bot.send_photo(MY_CHAT_ID, msg.photo)

            time.sleep(20)

        except Exception as e:
            print("❌ DM Error:", e)
            time.sleep(30)

# --- أوامر التليجرام ---

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🔥 البوت شغال!\n\nالأوامر:\n/profile user\n/story user\n/info user\n/posts user")

# صورة الحساب
@bot.message_handler(commands=['profile'])
def profile(msg):
    try:
        user = msg.text.split()[1]
        info = cl.user_info_by_username(user)
        bot.send_photo(msg.chat.id, info.profile_pic_url)
    except:
        bot.reply_to(msg, "❌ خطأ بالأمر")

# معلومات حساب
@bot.message_handler(commands=['info'])
def info(msg):
    try:
        user = msg.text.split()[1]
        u = cl.user_info_by_username(user)

        text = f"""
👤 الاسم: {u.full_name}
📛 اليوزر: {u.username}
👥 المتابعين: {u.follower_count}
➡️ يتابع: {u.following_count}
📝 البايو: {u.biography}
"""
        bot.send_message(msg.chat.id, text)
    except:
        bot.reply_to(msg, "❌ خطأ بالأمر")

# ستوري
@bot.message_handler(commands=['story'])
def story(msg):
    try:
        user = msg.text.split()[1]
        user_id = cl.user_id_from_username(user)
        stories = cl.user_stories(user_id)

        if not stories:
            bot.reply_to(msg, "❌ ماكو ستوري")
            return

        for s in stories:
            if s.video_url:
                bot.send_video(msg.chat.id, s.video_url)
            else:
                bot.send_photo(msg.chat.id, s.thumbnail_url)

    except:
        bot.reply_to(msg, "❌ خطأ بالأمر")

# منشورات
@bot.message_handler(commands=['posts'])
def posts(msg):
    try:
        user = msg.text.split()[1]
        user_id = cl.user_id_from_username(user)
        medias = cl.user_medias(user_id, 3)

        for m in medias:
            if m.video_url:
                bot.send_video(msg.chat.id, m.video_url)
            else:
                bot.send_photo(msg.chat.id, m.thumbnail_url)

    except:
        bot.reply_to(msg, "❌ خطأ بالأمر")

# تشغيل
if login():
    bot.send_message(MY_CHAT_ID, "🚀 البوت اشتغل ويراقب الدايركت")
    threading.Thread(target=monitor_dm, daemon=True).start()
else:
    bot.send_message(MY_CHAT_ID, "❌ فشل تسجيل الدخول")

bot.infinity_polling(skip_pending=True)
