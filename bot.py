from telebot import TeleBot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get token from environment variable
TOKEN = os.getenv('TOKEN')

# Get admins from environment variable
ADMINS = os.getenv('ADMINS').split(',')

# setup
app = TeleBot(TOKEN)

# ANSI escape codes for bold and red text in the terminal
BOLD_RED = '\033[1;31m'
RESET = '\033[0m'

# Dictionary to track warning counts for users
user_warnings = {}

# Warning limit before banning the user
WARNING_LIMIT = 3

def check_message(type, message):
    user_id = message.from_user.id

    # Skip admins from being checked
    if user_id in ADMINS:
        return

    # Check getChatMember, check if user is creator or administrator
    chat_member = app.get_chat_member(message.chat.id, user_id)

    if chat_member.status in ['creator', 'administrator']:
        return

    # Check for left anonymous bot case
    if chat_member.status == 'left' and chat_member.user.username == 'GroupAnonymousBot':
        return

    # If a link or username is found in the message, send a warning
    if any(term in message.text for term in ['@', 't.me', 'http://', 'https://', '.com', '.ir']):
        print(f"{BOLD_RED}Found links in message text{RESET}")
        
        # Increment user's warning count
        if user_id not in user_warnings:
            user_warnings[user_id] = 0
        user_warnings[user_id] += 1

        # If user has exceeded the warning limit, ban them
        if user_warnings[user_id] >= WARNING_LIMIT:
            app.send_message(message.chat.id, f"User @{message.from_user.username} has been banned for sharing links repeatedly.")
            app.kick_chat_member(message.chat.id, user_id)
        else:
            remaining_warnings = WARNING_LIMIT - user_warnings[user_id]
            app.send_message(message.chat.id, f"⚠️ @{message.from_user.username}, please refrain from sharing links. You have {remaining_warnings} warnings left before getting banned.")
        
        # Delete the violating message
        app.delete_message(message.chat.id, message.message_id)

# Edit message listener
@app.edited_message_handler(func=lambda message: True)
def edit_message(message):
    check_message("edit", message)

# New message listener
@app.message_handler(func=lambda message: True)
def new_message(message):
    check_message("new", message)

# Keep alive
if __name__ == '__main__':
    app.infinity_polling()
