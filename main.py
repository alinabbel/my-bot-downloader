import telebot
import instaloader
import time
import threading
from keep_alive import keep_alive

# --- بياناتك الجديدة ---
TOKEN = '8607922156:AAFHV0f9aHoNH0aQcusL_4oo0NFIhH_B9Ds'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = '486391606'

bot = telebot.TeleBot(TOKEN)

# حذف أي اتصالات قديمة نهائياً
try:
    bot.remove_webhook()
    bot.delete_webhook()
    time.sleep(2)
except:
    pass

# محاكاة بصمة سفاري على آيفون
L = instaloader.Instaloader(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1")

keep_alive()

def login_insta():
    try:
        L.login(INSTA_USER, INSTA_PASS)
        print("✅ البوت سجل دخول مباشر بهوية آيفون!")
        return True
    except Exception as e:
        print(f"❌ الإنستا بعده شاك: {e}")
        return False

def check_messages():
    while True:
        try:
            # مراقبة الدايركت (مثل الفيديو)
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
                                bot.send_video(MY_CHAT_ID, post.video_url, caption="وصلك الفيديو وحملته فوراً! 🔥")
            time.sleep(45)
        except:
            time.sleep(60)

# تشغيل النظام
if login_insta():
    threading.Thread(target=check_messages, daemon=True).start()

bot.infinity_polling(skip_pending=True)
