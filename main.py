import telebot
import time
import threading
import requests
import json
import os
from keep_alive import keep_alive

# — بياناتك —

TOKEN = ‘8607922156:AAFHV0f9aHoNH0aQcusL_4oo0NFIhH_B9Ds’
INSTA_USER = ‘bhsfso76268’
INSTA_PASS = ‘0099ali1122’
MY_CHAT_ID = ‘486391606’

bot = telebot.TeleBot(TOKEN)

# حذف webhook قديم

try:
bot.remove_webhook()
time.sleep(2)
except:
pass

# ===== إنستاجرام API =====

from instagram_private_api import Client, ClientCompatPatch

api = None
last_seen_items = set()  # لتتبع الرسائل اللي شفناها

def login_instagram():
global api
try:
api = Client(INSTA_USER, INSTA_PASS, auto_patch=True, drop_incompat_keys=False)
print(“✅ سجلنا دخول إنستاجرام بنجاح!”)
return True
except Exception as e:
print(f”❌ فشل تسجيل الدخول: {e}”)
return False

def download_and_send(url, caption=””):
“”“تحميل الميديا وإرسالها لتيليجرام”””
try:
headers = {
‘User-Agent’: ‘Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15’
}
response = requests.get(url, headers=headers, timeout=30)

```
    if response.status_code == 200:
        # تحديد نوع الملف
        content_type = response.headers.get('content-type', '')
        
        if 'video' in content_type or url.endswith('.mp4'):
            bot.send_video(MY_CHAT_ID, response.content, caption=caption)
            print(f"✅ أرسلنا فيديو!")
        else:
            bot.send_photo(MY_CHAT_ID, response.content, caption=caption)
            print(f"✅ أرسلنا صورة!")
except Exception as e:
    print(f"❌ خطأ في التحميل: {e}")
    # إرسال اللينك مباشرة كبديل
    try:
        bot.send_message(MY_CHAT_ID, f"🔗 {caption}\n{url}")
    except:
        pass
```

def process_inbox_item(item):
“”“معالجة كل رسالة واردة”””
try:
item_id = item.get(‘item_id’, ‘’)

```
    if item_id in last_seen_items:
        return
    last_seen_items.add(item_id)
    
    item_type = item.get('item_type', '')
    
    # ريلز أو فيديو
    if item_type == 'media_share':
        media = item.get('media', {})
        media_type = media.get('media_type', 0)
        user = media.get('user', {}).get('username', 'unknown')
        
        if media_type == 2:  # فيديو
            versions = media.get('video_versions', [])
            if versions:
                url = versions[0].get('url', '')
                download_and_send(url, f"🎬 ريلز من @{user}")
                
        elif media_type == 1:  # صورة
            candidates = media.get('image_versions2', {}).get('candidates', [])
            if candidates:
                url = candidates[0].get('url', '')
                download_and_send(url, f"📸 صورة من @{user}")
                
        elif media_type == 8:  # كاروسيل
            items = media.get('carousel_media', [])
            for i, carousel_item in enumerate(items):
                if carousel_item.get('media_type') == 2:
                    versions = carousel_item.get('video_versions', [])
                    if versions:
                        download_and_send(versions[0]['url'], f"🎬 كاروسيل {i+1} من @{user}")
                else:
                    candidates = carousel_item.get('image_versions2', {}).get('candidates', [])
                    if candidates:
                        download_and_send(candidates[0]['url'], f"📸 كاروسيل {i+1} من @{user}")

    # ستوري
    elif item_type == 'reel_share':
        reel = item.get('reel_share', {})
        media = reel.get('media', {})
        user = media.get('user', {}).get('username', 'unknown')
        media_type = media.get('media_type', 0)
        
        if media_type == 2:
            versions = media.get('video_versions', [])
            if versions:
                download_and_send(versions[0]['url'], f"📖 ستوري من @{user}")
        elif media_type == 1:
            candidates = media.get('image_versions2', {}).get('candidates', [])
            if candidates:
                download_and_send(candidates[0]['url'], f"📖 ستوري من @{user}")

    # لينك عادي
    elif item_type == 'link':
        link_url = item.get('link', {}).get('text', '')
        if 'instagram.com' in link_url:
            bot.send_message(MY_CHAT_ID, f"🔗 وصلك لينك:\n{link_url}")

except Exception as e:
    print(f"❌ خطأ في معالجة الرسالة: {e}")
```

def monitor_inbox():
“”“مراقبة الدايركت كل 30 ثانية”””
global api
print(“👀 بدأنا مراقبة الدايركت…”)

```
while True:
    try:
        inbox = api.direct_v2_inbox()
        threads = inbox.get('inbox', {}).get('threads', [])
        
        for thread in threads:
            # فقط الخيوط اللي فيها رسائل غير مقروءة
            if thread.get('read_state') != 0:
                continue
                
            items = thread.get('items', [])
            for item in items:
                process_inbox_item(item)
                
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ خطأ في المراقبة: {e}")
        time.sleep(60)
        # إعادة تسجيل الدخول
        try:
            login_instagram()
        except:
            pass
```

# ===== تيليجرام =====

@bot.message_handler(commands=[‘start’])
def start(message):
bot.send_message(message.chat.id,
“👋 أهلاً!\n\n”
“أنا شغال وأراقب الدايركت على إنستاجرام 👀\n”
“كل ما يوصلك ريلز أو ستوري أحولها لك هنا فوراً! 🔥\n\n”
f”Chat ID: `{message.chat.id}`”,
parse_mode=‘Markdown’
)

@bot.message_handler(commands=[‘status’])
def status(message):
status_text = “✅ متصل بإنستاجرام” if api else “❌ غير متصل”
bot.send_message(message.chat.id, f”الحالة: {status_text}”)

# ===== تشغيل البوت =====

keep_alive()

if login_instagram():
bot.send_message(MY_CHAT_ID, “✅ البوت شغال وجاهز!\nأرسل أي ريلز أو ستوري للدايركت على إنستاجرام وأحولها لك هنا 🔥”)
threading.Thread(target=monitor_inbox, daemon=True).start()
else:
bot.send_message(MY_CHAT_ID, “❌ فشل تسجيل الدخول لإنستاجرام، راجع البيانات”)

print(“🤖 البوت يشتغل…”)
bot.infinity_polling(skip_pending=True)
