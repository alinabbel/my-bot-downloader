import telebot
import instaloader
import time
import os
import threading
from keep_alive import keep_alive

# --- بياناتك ---
TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = '486391606'

# تشغيل البوت مع حذف أي اتصال قديم فوراً
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook() # هذا السطر يحل مشكلة الـ 409 فوراً
time.sleep(2)

L = instaloader.Instaloader()
keep_alive()

def login_insta():
    try:
        # محاولة تسجيل دخول هادئة
        L.login(INSTA_USER, INSTA_PASS)
        print("✅ تم ربط انستا بنجاح!")
        return True
    except Exception as e:
        print(f"❌ خطأ انستا: {e}")
        return False

def check_messages():
    while True:
        try:
            for thread in L.get_threads():
                if thread.unread_count > 0:
                    for item in thread.get_items():
                        url = ""
                        if item.item_type == 'link':
                            url = item.link.get('url')
                        elif item.item_type == 'media_share':
                            url = f"https://www.instagram.com/reels/{item.media.shortcode}/"
                        
                        if url and 'instagram.com' in url:
                            shortcode = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
                            if "?" in shortcode: shortcode = shortcode.split("?")[0]
                            post = instaloader.Post.from_shortcode(L.context, shortcode)
                            if post.is_video:
                                bot.send_video(MY_CHAT_ID, post.video_url, caption="حملته إلك من الدايركت! 🔥")
            time.sleep(30)
        except:
            time.sleep(60)

# تشغيل المراقبة
if login_insta():
    threading.Thread(target=check_messages, daemon=True).start()

# تشغيل البوت مع تجاوز أخطاء التضارب
bot.infinity_polling(timeout=10, long_polling_timeout=5)
