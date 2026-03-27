import telebot
import yt_dlp
import os

TOKEN = '8607922156:AAFHV0f9aHoNH0aQcusL_4oo0NFIhH_B9Ds'

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

MAX_SIZE = 50 * 1024 * 1024  # 50MB

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🔥 دز أي رابط وأنا أحمله بأفضل جودة وبشكل ذكي 😎")

@bot.message_handler(func=lambda m: "http" in m.text)
def download(msg):
    url = msg.text.strip()
    bot.reply_to(msg, "⏳ جاري التحميل...")

    formats_try = [
        'bestvideo+bestaudio',  # أعلى جودة
        'best',                 # بدون دمج
        'mp4',                  # صيغة جاهزة
        'worst'                 # آخر حل 😂
    ]

    file_path = None

    for fmt in formats_try:
        try:
            ydl_opts = {
                'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
                'format': fmt,
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if file_path and os.path.exists(file_path):
                break

        except Exception as e:
            print(f"❌ فشل بصيغة {fmt}: {e}")
            continue

    if not file_path or not os.path.exists(file_path):
        bot.reply_to(msg, "❌ ماكدر احمل الرابط")
        return

    size = os.path.getsize(file_path)

    try:
        with open(file_path, 'rb') as f:
            if size > MAX_SIZE:
                bot.send_document(msg.chat.id, f)
            else:
                bot.send_video(msg.chat.id, f)
    except Exception as e:
        bot.reply_to(msg, f"❌ خطأ بالإرسال:\n{e}")

    os.remove(file_path)

bot.infinity_polling()
