import telebot
from telebot import types
import yt_dlp
import requests
import os

TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'
RAPID_API_KEY = '8058182bcdmsh68f7c04d403ca05p1dc715jsn335a6b983b66'
RAPID_HOST = 'instagram-downloader-scraper-reels-igtv-posts-stories.p.rapidapi.com'

bot = telebot.TeleBot(TOKEN)

def get_headers():
    return {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': RAPID_HOST
    }

def download_file(url, fname):
    r = requests.get(url, stream=True)
    with open(fname, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return fname

def download_instagram_post(url, chat_id):
    try:
        response = requests.get(
            f'https://{RAPID_HOST}/post',
            headers=get_headers(),
            params={'url': url}
        )
        data = response.json()
        files = []

        # بوست فيديو أو ريلز
        if data.get('video'):
            fname = f'insta_{chat_id}.mp4'
            download_file(data['video'], fname)
            files.append(fname)

        # صورة مفردة
        elif data.get('image'):
            fname = f'insta_{chat_id}.jpg'
            download_file(data['image'], fname)
            files.append(fname)

        # مجموعة صور/فيديوهات
        elif data.get('media'):
            for i, item in enumerate(data['media']):
                if item.get('video'):
                    fname = f'insta_{chat_id}_{i}.mp4'
                    download_file(item['video'], fname)
                elif item.get('image'):
                    fname = f'insta_{chat_id}_{i}.jpg'
                    download_file(item['image'], fname)
                else:
                    continue
                files.append(fname)

        return files
    except:
        return []

def download_instagram_stories(username, chat_id):
    try:
        response = requests.get(
            f'https://{RAPID_HOST}/stories',
            headers=get_headers(),
            params={'username': username}
        )
        data = response.json()
        files = []

        items = data.get('stories') or data.get('items') or data.get('data') or []
        for i, item in enumerate(items):
            if item.get('video'):
                fname = f'story_{chat_id}_{i}.mp4'
                download_file(item['video'], fname)
            elif item.get('image'):
                fname = f'story_{chat_id}_{i}.jpg'
                download_file(item['image'], fname)
            else:
                continue
            files.append(fname)

        return files
    except:
        return []

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
                    try:
                        ydl2.download([entry['webpage_url']])
                        fname = ydl2.prepare_filename(entry)
                        if os.path.exists(fname):
                            files.append(fname)
                    except:
                        continue
            return files
        else:
            ydl.download([url])
            fname = ydl.prepare_filename(info)
            return [fname] if os.path.exists(fname) else []

def send_files(chat_id, files, msg_id):
    if not files:
        bot.edit_message_text("ما قدرت أجيب الملف، جرب رابط ثاني", chat_id, msg_id)
        return
    for f in files:
        if not os.path.exists(f):
            continue
        ext = f.split('.')[-1].lower()
        with open(f, 'rb') as media:
            if ext in ['mp4', 'mov', 'avi', 'mkv']:
                bot.send_video(chat_id, media)
            elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                bot.send_photo(chat_id, media)
            else:
                bot.send_document(chat_id, media)
        os.remove(f)
    bot.delete_message(chat_id, msg_id)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    url = message.text.strip()
    chat_id = message.chat.id

    if "http" in url:
        msg = bot.send_message(chat_id, "خادمك.. ثواني وأجيبلك الطلب 🏃‍♂️")
        try:
            if "instagram.com" in url:
                files = download_instagram_post(url, chat_id)
                if files:
                    send_files(chat_id, files, msg.message_id)
                    return
            files = download_media(url, chat_id)
            send_files(chat_id, files, msg.message_id)
        except Exception as e:
            bot.edit_message_text("صار عندي خلل بهذا الرابط.. جرب غيره يا طيب", chat_id, msg.message_id)
    else:
        username = url.replace("@", "")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("المعلومات 📋", callback_data=f"info_{username}"))
        markup.add(types.InlineKeyboardButton("الستوريات 📸", callback_data=f"stories_{username}"))
        bot.reply_to(message, f"شتريد أسحب من @{username}؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stories_'))
def handle_stories(call):
    username = call.data.replace('stories_', '')
    chat_id = call.message.chat.id
    msg = bot.send_message(chat_id, f"جاري سحب ستوريات @{username} 📸")
    files = download_instagram_stories(username, chat_id)
    if files:
        send_files(chat_id, files, msg.message_id)
    else:
        bot.edit_message_text(f"ما لقيت ستوريات لـ @{username} أو الحساب خاص", chat_id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def handle_info(call):
    username = call.data.replace('info_', '')
    chat_id = call.message.chat.id
    try:
        response = requests.get(
            f'https://{RAPID_HOST}/profile',
            headers=get_headers(),
            params={'username': username}
        )
        data = response.json()
        info = f"""
📋 معلومات @{username}
👤 الاسم: {data.get('full_name', 'غير متاح')}
📝 البايو: {data.get('biography', 'غير متاح')}
👥 المتابعين: {data.get('followers', 0):,}
➡️ يتابع: {data.get('following', 0):,}
📸 المنشورات: {data.get('posts', 0):,}
🔒 خاص: {'نعم' if data.get('is_private') else 'لا'}
"""
        bot.send_message(chat_id, info)
    except:
        bot.send_message(chat_id, "ما قدرت أجيب المعلومات، تأكد من اليوزر")

bot.polling()
