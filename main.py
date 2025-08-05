import os
import re
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    Filters
)

# Initialize
BOT_TOKEN = os.getenv('BOT_TOKEN')
users = {}  # Format: {user_id: {config}}

class UserConfig:
    def __init__(self):
        self.sources = []
        self.targets = []
        self.filters = {
            'begin_text': '',
            'end_text': '',
            'blacklist': [],
            'whitelist': [],
            'delay': 0,
            'should_edit': False,
            'should_delete': False,
            'allowed_users': []
        }
        self.is_active = False
        self.is_premium = False

# ========================
# COMMAND HANDLERS
# ========================

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = UserConfig()
    
    update.message.reply_text(
        "🔄 Auto Forwarder Bot\n\n"
        "/work - Start forwarding\n"
        "/stop - Pause forwarding\n"
        "/config - View settings\n"
        "/upgrade - Premium features",
        reply_markup=main_menu()
    )

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Config", callback_data='config_menu')],
        [InlineKeyboardButton("🌟 Upgrade", callback_data='upgrade')]
    ])

# ========================
# TEXT MODIFICATION COMMANDS
# ========================

def begin_text(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['begin_text'] = ' '.join(context.args)
    update.message.reply_text(f"✅ Prepending text: {' '.join(context.args)}")

def end_text(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['end_text'] = ' '.join(context.args)
    update.message.reply_text(f"✅ Appending text: {' '.join(context.args)}")

# ========================
# FILTER COMMANDS
# ========================

def blacklist(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['blacklist'].extend(context.args)
    update.message.reply_text(f"🚫 Blacklisted: {', '.join(context.args)}")

def whitelist(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['whitelist'].extend(context.args)
    update.message.reply_text(f"✅ Whitelisted: {', '.join(context.args)}")

def filter_users(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['allowed_users'].extend(context.args)
    update.message.reply_text(f"👥 Allowed users: {', '.join(context.args)}")

# ========================
# CONFIG MANAGEMENT
# ========================

def delay(update: Update, context: CallbackContext):
    try:
        delay_sec = int(context.args[0])
        users[update.effective_user.id].filters['delay'] = delay_sec
        update.message.reply_text(f"⏳ Delay set: {delay_sec}s")
    except (IndexError, ValueError):
        update.message.reply_text("⚠️ Usage: /delay <seconds>")

def should_edit(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['should_edit'] = True
    update.message.reply_text("✏️ Edit mode enabled")

def should_delete(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['should_delete'] = True
    update.message.reply_text("🗑️ Delete mode enabled")

# ========================
# REMOVAL COMMANDS
# ========================

def remove_whitelist(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['whitelist'] = []
    update.message.reply_text("✅ Whitelist cleared")

def remove_blacklist(update: Update, context: CallbackContext):
    users[update.effective_user.id].filters['blacklist'] = []
    update.message.reply_text("✅ Blacklist cleared")

def reset_config(update: Update, context: CallbackContext):
    users[update.effective_user.id] = UserConfig()
    update.message.reply_text("🔄 All settings reset")

def remove_session(update: Update, context: CallbackContext):
    users.pop(update.effective_user.id, None)
    update.message.reply_text("🔒 Logged out. Use /start to begin again.")

# ========================
# CORE FUNCTIONALITY
# ========================

def work(update: Update, context: CallbackContext):
    users[update.effective_user.id].is_active = True
    update.message.reply_text("🟢 Forwarding STARTED")

def stop(update: Update, context: CallbackContext):
    users[update.effective_user.id].is_active = False
    update.message.reply_text("🔴 Forwarding STOPPED")

def restart(update: Update, context: CallbackContext):
    stop(update, context)
    work(update, context)

# ========================
# BUTTON HANDLERS
# ========================

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'config_menu':
        show_config_menu(update.effective_user.id, query)
    elif query.data == 'upgrade':
        upgrade(update, context)

def show_config_menu(user_id, query):
    user = users.get(user_id, UserConfig())
    query.edit_message_text(
        f"⚙️ Current Configuration:\n"
        f"Active: {'🟢' if user.is_active else '🔴'}\n"
        f"Sources: {len(user.sources)}\n"
        f"Targets: {len(user.targets)}\n"
        f"Filters: {len(user.filters['blacklist'] + len(user.filters['whitelist'])}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛑 Stop", callback_data='stop'),
             InlineKeyboardButton("🔄 Restart", callback_data='restart')],
            [InlineKeyboardButton("🗑️ Reset All", callback_data='reset')]
        ])
    )

if __name__ == '__main__':
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    # Add all command handlers
    commands = [
        ('start', start),
        ('work', work),
        ('stop', stop),
        ('restart', restart),
        ('begin_text', begin_text),
        ('end_text', end_text),
        ('blacklist', blacklist),
        ('whitelist', whitelist),
        ('delay', delay),
        ('should_edit', should_edit),
        ('should_delete', should_delete),
        ('rem_whitelist', remove_whitelist),
        ('rem_blacklist', remove_blacklist),
        ('reset_config', reset_config),
        ('remove_session', remove_session),
        ('filter_users', filter_users)
    ]
    
    for cmd, handler in commands:
        dp.add_handler(CommandHandler(cmd, handler))
    
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot is running with all features!")
    updater.start_polling()
    updater.idle()
