import telebot
import instaloader
import time
import threading
from keep_alive import keep_alive

# --- إعداداتك ---
TOKEN = '8607922156:AAEAzr39wISJ5QumopaGwmKIT2GNP2ruE8s'
INSTA_USER = 'bhsfso76268'
INSTA_PASS = '0099ali1122'
MY_CHAT_ID = '486391606'

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
L = instaloader.Instaloader()
keep_alive()

def silent_login():
    try:
        # يحاول يدخل "سكوتي" بدون ما يطلب تأكيد جديد
        L.load_session_from_file(INSTA_USER)
        print("✅ دخلت مباشر باستخدام الجلسة المحفوظة!")
    except:
        try:
            L.login(INSTA_USER, INSTA_PASS)
            L.save_session_to_file()
            print("✅ سجلت دخول وحفظت الجلسة للمرات القادمة.")
        except Exception as e:
            print(f"❌ الإنستا بعده قافل: {e}")
            return False
    return True

def monitor_direct():
    while True:
        try:
            # مراقبة "هادئة" للدايركت
            for thread in L.get_threads():
                if thread.unread_count > 0:
                    for item in thread.get_items():
                        # منطق التحميل هنا...
                        pass
            time.sleep(60) # نزيد الوقت حتى ما يشك بينا إنستا
        except:
            time.sleep(120)

if silent_login():
    threading.Thread(target=monitor_direct, daemon=True).start()

bot.infinity_polling(skip_pending=True)
