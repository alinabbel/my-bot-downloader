import telebot
from telebot import types
import yt_dlp
import instaloader
import os
from keep_alive import keep_alive # تأكد إنك سويت ملف keep_alive.py مثل ما علمتك

# --- البيانات الخاصة بك ---
TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
# -------------------------

bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader()

# تشغيل نظام البقاء حياً (Keep Alive) لـ Replit
keep_alive()

# تسجيل دخول انستا
try:
    L.load_session_from_file(INSTA_USER)
    print("✅ تم تحميل الجلسة بنجاح")
except:
    try:
        L.login(INSTA_USER, INSTA_PASS)
        L.save_session_to_file()
        print("✅ تم تسجيل الدخول وحفظ الجلسة")
    except Exception as e:
        print("❌ فشل تسجيل الدخول في انستقرام:", e)

user_links = {}

# كيبورد إنستا
def insta_keyboard(username):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 معلومات الحساب", callback_data=f"info_{username}"))
    markup.add(types.InlineKeyboardButton("🖼 صورة البروفايل", callback_data=f"pic_{username}"))
    markup.add(types.InlineKeyboardButton("📸 الستوريات", callback_data=f"stories_{username}"))
    markup.add(types.InlineKeyboardButton("⭐ الهايلايت", callback_data=f"highlights_{username}"))
    return markup

# كيبورد التحميل العام
def download_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎬 فيديو", callback_data="video"),
        types.InlineKeyboardButton("🎧 صوت (MP3)", callback_data="audio")
    )
    markup.add(types.InlineKeyboardButton("🖼 صور", callback_data="photo"))
    return markup

# وظيفة التحميل باستخدام yt-dlp
def download_media(url, chat_id, mode):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'file_{chat_id}_%(title)s.%(ext)s',
        'quiet': True,
    }

    if mode == "audio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    files = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if 'entries' in info:
            for entry in info['entries']:
                files.append(ydl.prepare_filename(entry))
        else:
            files.append(ydl.prepare_filename(info))
    return files

@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    text = msg.text.strip()
    chat_id = msg.chat.id

    if "http" in text:
        user_links[chat_id] = text
        bot.send_message(chat_id, "خادمك.. شتريد أحملك من هذا الرابط؟ 👇", reply_markup=download_keyboard())
    else:
        username = text.replace("@", "")
        bot.send_message(chat_id, f"شنو تريد أسحبلك من @{username}؟ 👇", reply_markup=insta_keyboard(username))

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    data = call.data

    try:
        if "_" in data:
            action, username = data.split("_", 1)
            bot.answer_callback_query(call.id, "جاري جلب البيانات من انستا..")
            profile = instaloader.Profile.from_username(L.context, username)

            if action == "info":
                text = f"👤 الاسم: {profile.full_name}\n📛 اليوزر: {profile.username}\n👥 المتابعين: {profile.followers}\n📝 البايو: {profile.biography}"
                bot.send_message(chat_id, text)
            elif action == "pic":
                bot.send_photo(chat_id, profile.profile_pic_url)
            elif action == "stories":
                for story in L.get_stories(userids=[profile.userid]):
                    for item in story.get_items():
                        if item.is_video: bot.send_video(chat_id, item.video_url)
                        else: bot.send_photo(chat_id, item.display_url)
            elif action == "highlights":
                for highlight in L.get_highlights(profile):
                    for item in highlight.get_items():
                        if item.is_video: bot.send_video(chat_id, item.video_url)
                        else: bot.send_photo(chat_id, item.display_url)
        else:
            mode = data
            url = user_links.get(chat_id)
            if not url:
                bot.send_message(chat_id, "الرابط ضاع مني، ممكن ترجع تدزه؟")
                return

            wait = bot.send_message(chat_id, "ثواني ويكون طلبك عندك.. دا أحمل 🔥")
            files = download_media(url, chat_id, mode)

            for file in files:
                with open(file, 'rb') as f:
                    if file.endswith(('.jpg', '.png', '.jpeg')): bot.send_photo(chat_id, f)
                    elif mode == "audio": bot.send_audio(chat_id, f)
                    else: bot.send_video(chat_id, f)
                if os.path.exists(file): os.remove(file)

            bot.delete_message(chat_id, wait.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(chat_id, "اعتذر منك، صار خطأ بالتحميل 💔")

print("🤖 البوت شغال هسة..")
bot.polling(none_stop=True)
