import telebot
import yt_dlp
import os

TOKEN = '8607922156:AAFHV0f9aHoNH0aQcusL_4oo0NFIhH_B9Ds'

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# حجم 50MB
MAX_SIZE = 50 * 1024 * 1024

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg,
        "🔥 دز رابط لأي فيديو\n\n"
        "🎬 تحميل فيديو: بس دز الرابط\n"
        "🎧 تحميل صوت: اكتب /audio + الرابط"
    )

# تحميل فيديو
@bot.message_handler(func=lambda m: "http" in m.text and not m.text.startswith("/audio"))
def download_video(msg):
    url = msg.text.strip()
    bot.reply_to(msg, "⏳ جاري تحميل الفيديو بأعلى جودة...")

    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            if not file_path.endswith(".mp4"):
                file_path = file_path.rsplit(".", 1)[0] + ".mp4"

        size = os.path.getsize(file_path)

        with open(file_path, 'rb') as f:
            if size > MAX_SIZE:
                bot.send_document(msg.chat.id, f)
            else:
                bot.send_video(msg.chat.id, f)

        os.remove(file_path)

    except Exception as e:
        bot.reply_to(msg, f"❌ خطأ:\n{e}")

# تحميل صوت
@bot.message_handler(commands=['audio'])
def download_audio(msg):
    try:
        url = msg.text.split(" ", 1)[1]
    except:
        bot.reply_to(msg, "❌ اكتب /audio + الرابط")
        return

    bot.reply_to(msg, "⏳ جاري تحميل الصوت...")

    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            file_path = file_path.rsplit(".", 1)[0] + ".mp3"

        with open(file_path, 'rb') as f:
            bot.send_audio(msg.chat.id, f)

        os.remove(file_path)

    except Exception as e:
        bot.reply_to(msg, f"❌ خطأ:\n{e}")

bot.infinity_polling()
