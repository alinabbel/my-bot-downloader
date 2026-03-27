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
# --------------

bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader()
keep_alive()

def login_insta():
    try:
        # محاولة تحميل الجلسة إذا كانت موجودة سابقاً لتجنب الحظر
        L.load_session_from_file(INSTA_USER)
    except FileNotFoundError:
        # إذا أول مرة، يسجل دخول ويحفظ الجلسة
        L.login(INSTA_USER, INSTA_PASS)
        L.save_session_to_file()
    print("✅ تم ربط حساب الانستا بنجاح!")

def check_messages():
    while True:
        try:
            for thread in L.get_threads():
                if thread.unread_count > 0:
                    for item in thread.get_items():
                        # التحقق من وجود فيديو (ريلز أو ستوري مشارك)
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
                                bot.send_video(MY_CHAT_ID, post.video_url, caption="وصلك الفيديو بالدايركت وحملته إلك! 🔥")
                                # تنبيه: المكتبة لا تدعم "تحديد كـ مقروء" بسهولة، سنعتمد على الوقت
            time.sleep(30)
        except Exception as e:
            print(f"جاري إعادة المحاولة... {e}")
            time.sleep(60)

# تشغيل العمليات
try:
    login_insta()
    threading.Thread(target=check_messages, daemon=True).start()
except:
    print("فشل الدخول، يرجى التأكد من الحساب")

bot.polling(none_stop=True)
