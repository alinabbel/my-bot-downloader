import telebot
import instaloader
import time
import os
import threading
from keep_alive import keep_alive

# --- الإعدادات الخاصة بك ---
TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = '486391606' # الأيدي مالتك اللي دزيته
# -------------------------

bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader()
keep_alive()

# تسجيل دخول انستا
try:
    L.login(INSTA_USER, INSTA_PASS)
    print("✅ البوت سجل دخول بالانستا وبدأ المراقبة...")
    bot.send_message(MY_CHAT_ID, "✅ البوت اشتغل وبدأ يراقب رسائل الدايركت مالتك!")
except Exception as e:
    print(f"❌ خطأ دخول انستا: {e}")

def check_insta_messages():
    while True:
        try:
            # يفتح الرسائل الخاصة (Direct Messages)
            for thread in L.get_threads():
                if thread.unread_count > 0:
                    for item in thread.get_items():
                        # إذا كانت الرسالة عبارة عن رابط (Link)
                        if item.item_type == 'link' or item.item_type == 'media_share':
                            url = item.link.get('url') if item.item_type == 'link' else f"https://www.instagram.com/reels/{item.media.shortcode}/"
                            
                            if 'instagram.com' in url:
                                # سحب كود الفيديو
                                shortcode = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
                                if "?" in shortcode: shortcode = shortcode.split("?")[0]
                                
                                post = instaloader.Post.from_shortcode(L.context, shortcode)
                                if post.is_video:
                                    bot.send_video(MY_CHAT_ID, post.video_url, caption="وصلك فيديو جديد من الدايركت! 📥")
            
            time.sleep(30) # يشيك كل 30 ثانية
        except Exception as e:
            print(f"حدث خطأ أثناء المراقبة: {e}")
            time.sleep(30)

# تشغيل المراقبة في خلفية السيرفر
threading.Thread(target=check_insta_messages, daemon=True).start()

bot.polling(none_stop=True)
