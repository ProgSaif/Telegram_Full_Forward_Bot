import os
import logging
from telegram import Update, Message
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Storage structure
class UserConfig:
    def __init__(self):
        self.sources = set()  # Using sets to avoid duplicates
        self.targets = set()
        self.is_active = False
        self.filters = {
            'blacklist': set(),
            'whitelist': set(),
            'delay': 0
        }

users = {}  # {user_id: UserConfig}

# ========================
# CORE FORWARDING LOGIC
# ========================
async def forward_message(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        if user_id not in users or not users[user_id].is_active:
            return

        config = users[user_id]
        message = update.effective_message

        # Check if message is from a source channel
        if message.chat.id not in config.sources:
            return

        # Apply filters
        if config.filters['blacklist'] and any(word in message.text for word in config.filters['blacklist']):
            return

        if config.filters['whitelist'] and not any(word in message.text for word in config.filters['whitelist']):
            return

        # Forward to all target channels
        for target in config.targets:
            await message.copy(chat_id=target)
            logger.info(f"Forwarded message to {target}")

    except Exception as e:
        logger.error(f"Forwarding error: {e}")

# ========================
# CHANNEL MANAGEMENT
# ========================
def add_source(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users.setdefault(user_id, UserConfig()).sources.add(update.effective_chat.id)
        update.message.reply_text(f"✅ Added as source: {update.effective_chat.title}")
    except Exception as e:
        logger.error(f"Add source error: {e}")

def add_target(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users.setdefault(user_id, UserConfig()).targets.add(int(context.args[0]))
        update.message.reply_text(f"✅ Added target: {context.args[0]}")
    except (IndexError, ValueError):
        update.message.reply_text("⚠️ Usage: /add_target <channel_id>")
    except Exception as e:
        logger.error(f"Add target error: {e}")

# ========================
# COMMAND HANDLERS
# ========================
def start(update: Update, context: CallbackContext):
    users[update.effective_user.id] = UserConfig()
    update.message.reply_text(
        "🤖 Auto Forwarder Bot\n\n"
        "/add_source - Add current channel as source\n"
        "/add_target <id> - Add target channel\n"
        "/work - Start forwarding\n"
        "/stop - Pause forwarding"
    )

def work(update: Update, context: CallbackContext):
    users[update.effective_user.id].is_active = True
    update.message.reply_text("🟢 Forwarding STARTED")

def stop(update: Update, context: CallbackContext):
    users[update.effective_user.id].is_active = False
    update.message.reply_text("🔴 Forwarding STOPPED")

# ========================
# BOT SETUP
# ========================
def main():
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher

        # Command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("work", work))
        dp.add_handler(CommandHandler("stop", stop))
        dp.add_handler(CommandHandler("add_source", add_source))
        dp.add_handler(CommandHandler("add_target", add_target))

        # Message handler for forwarding
        dp.add_handler(MessageHandler(Filters.all & ~Filters.command, forward_message))

        logger.info("Bot is running...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.critical(f"Startup failed: {e}")

if __name__ == '__main__':
    main()
