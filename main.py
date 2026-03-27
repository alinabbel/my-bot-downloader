import telebot
import instaloader
import time
import threading
from keep_alive import keep_alive

# --- بياناتك ---
TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = '486391606'

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# محاكاة بصمة سفاري على آيفون (نفس اللي فتحت بيه هسة)
L = instaloader.Instaloader(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1")

keep_alive()

def login_insta():
    try:
        # محاولة الدخول بهوية سفاري
        L.login(INSTA_USER, INSTA_PASS)
        print("✅ أخيراً! السيرفر تنكر بهيئة سفاري ودخل بنجاح")
        return True
    except Exception as e:
        print(f"❌ الإنستا بعده شاك بالبصمة: {e}")
        return False

def check_messages():
    while True:
        try:
            # مراقبة الدايركت (نفس طريقتك بالفيديو)
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
                                bot.send_video(MY_CHAT_ID, post.video_url, caption="وصلك الفيديو بالدايركت وحملته! 🚀")
            time.sleep(40)
        except:
            time.sleep(60)

if login_insta():
    threading.Thread(target=check_messages, daemon=True).start()

bot.infinity_polling(skip_pending=True)
