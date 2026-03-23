import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'

bot = telebot.TeleBot(TOKEN)

def download_media(url, chat_id):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'file_{chat_id}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if 'entries' in info:
            files = []
            for i, entry in enumerate(info['entries']):
                opts = {
                    'format': 'best',
                    'outtmpl': f'file_{chat_id}_{i}.%(ext)s',
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(opts) as ydl2:
                    ydl2.download([entry['webpage_url']])
                    fname = ydl2.prepare_filename(entry)
                    if os.path.exists(fname):
                        files.append(fname)
            return files
        else:
            ydl.download([url])
            fname = ydl.prepare_filename(info)
            return [fname] if os.path.exists(fname) else []

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    url = message.text.strip()
    chat_id = message.chat.id

    if "http" in url:
        msg = bot.send_message(chat_id, "خادمك.. ثواني وأجيبلك الطلب 🏃‍♂️")
        
        try:
            files = download_media(url, chat_id)
            
            if not files:
                bot.edit_message_text("ما قدرت أجيب الملف، جرب رابط ثاني", chat_id, msg.message_id)
                return
            
            for f in files:
                ext = f.split('.')[-1].lower()
                with open(f, 'rb') as media:
                    if ext in ['mp4', 'mov', 'avi', 'mkv']:
                        bot.send_video(chat_id, media)
                    elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                        bot.send_photo(chat_id, media)
                    else:
                        bot.send_document(chat_id, media)
                os.remove(f)
            
            bot.delete_message(chat_id, msg.message_id)
        
        except Exception as e:
            bot.edit_message_text("صار عندي خلل بهذا الرابط.. جرب غيره يا طيب", chat_id, msg.message_id)

    else:
        username = url.replace("@", "")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("المعلومات 📋", callback_data=f"info_{username}"))
        markup.add(types.InlineKeyboardButton("الستوريات 📸", callback_data=f"stories_{username}"))
        bot.reply_to(message, f"شتريد أسحب من @{username}؟", reply_markup=markup)

bot.polling()
