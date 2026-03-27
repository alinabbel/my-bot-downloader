import telebot
import time
import threading
import requests
import json
import os
from keep_alive import keep_alive
from instagram_private_api import Client, ClientCompatPatch

# --- بياناتك ---
TOKEN = '8607922156:AAFHV0f9aHoNH0aQcusL_4oo0NFIhH_B9Ds'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = '486391606'

bot = telebot.TeleBot(TOKEN)

# حذف أي اتصال قديم
try:
    bot.remove_webhook()
    time.sleep(2)
except:
    pass

api = None
last_seen_items = set()

def login_instagram():
    global api
    try:
        # إعدادات محاكاة جهاز حقيقي لتجنب الحظر
        api = Client(INSTA_USER, INSTA_PASS, auto_patch=True)
        print("✅ سجلنا دخول إنستاجرام بنجاح!")
        return True
    except Exception as e:
        print(f"❌ فشل تسجيل الدخول: {e}")
        return False

def download_and_send(url, caption=""):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'video' in content_type or url.endswith('.mp4'):
                bot.send_video(MY_CHAT_ID, response.content, caption=caption)
            else:
                bot.send_photo(MY_CHAT_ID, response.content, caption=caption)
    except Exception as e:
        print(f"❌ خطأ في التحميل: {e}")

def process_inbox_item(item):
    try:
        item_id = item.get('item_id', '')
        if item_id in last_seen_items:
            return
        last_seen_items.add(item_id)
        
        item_type = item.get('item_type', '')
        
        if item_type == 'media_share':
            media = item.get('media', {})
            user = media.get('user', {}).get('username', 'unknown')
            if media.get('media_type') == 2: # فيديو
                url = media.get('video_versions', [{}])[0].get('url', '')
                download_and_send(url, f"🎬 ريلز من @{user}")
        
        elif item_type == 'link':
            link_url = item.get('link', {}).get('text', '')
            if 'instagram.com' in link_url:
                bot.send_message(MY_CHAT_ID, f"🔗 وصلك رابط:\n{link_url}")
    except Exception as e:
        print(f"❌ خطأ معالجة: {e}")

def monitor_inbox():
    global api
    print("👀 بدأت المراقبة...")
    while True:
        try:
            inbox = api.direct_v2_inbox()
            threads = inbox.get('inbox', {}).get('threads', [])
            for thread in threads:
                # إذا كانت الرسائل غير مقروءة
                if thread.get('read_state') == 0:
                    items = thread.get('items', [])
                    for item in items:
                        process_inbox_item(item)
            time.sleep(30)
        except Exception as e:
            print(f"❌ خطأ مراقبة: {e}")
            time.sleep(60)
            login_instagram()

keep_alive()

if login_instagram():
    bot.send_message(MY_CHAT_ID, "✅ البوت شغال وجاهز!")
    threading.Thread(target=monitor_inbox, daemon=True).start()
else:
    bot.send_message(MY_CHAT_ID, "❌ فشل تسجيل دخول انستا")

bot.infinity_polling(skip_pending=True)
