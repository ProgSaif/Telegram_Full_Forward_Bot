import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Configure logging for Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Simplified storage
class UserConfig:
    __slots__ = ['sources', 'targets', 'filters', 'is_active']  # Reduces memory usage
    
    def __init__(self):
        self.sources = []
        self.targets = []
        self.filters = {
            'blacklist': set(),  # Using sets for faster lookups
            'whitelist': set(),
            'delay': 0,
            'edit': False,
            'delete': False
        }
        self.is_active = False

users = {}

# ========================
# CORE COMMANDS (Crash-Proof)
# ========================
def start(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users[user_id] = UserConfig()
        
        update.message.reply_text(
            "🤖 Auto Forwarder Bot\n\n"
            "/work - Start forwarding\n"
            "/stop - Pause forwarding\n"
            "/config - View settings",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Config", callback_data='config')]
            ])
        )
    except Exception as e:
        logger.error(f"Start error: {e}")

def work(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users.setdefault(user_id, UserConfig()).is_active = True
        update.message.reply_text("🟢 Forwarding STARTED")
    except Exception as e:
        logger.error(f"Work error: {e}")

def stop(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users.setdefault(user_id, UserConfig()).is_active = False
        update.message.reply_text("🔴 Forwarding STOPPED")
    except Exception as e:
        logger.error(f"Stop error: {e}")

# ========================
# FILTER COMMANDS (Safe Implementation)
# ========================
def blacklist(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users.setdefault(user_id, UserConfig()).filters['blacklist'].update(context.args)
        update.message.reply_text(f"🚫 Added to blacklist: {', '.join(context.args)}")
    except Exception as e:
        logger.error(f"Blacklist error: {e}")

def whitelist(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users.setdefault(user_id, UserConfig()).filters['whitelist'].update(context.args)
        update.message.reply_text(f"✅ Added to whitelist: {', '.join(context.args)}")
    except Exception as e:
        logger.error(f"Whitelist error: {e}")

# ========================
# CONFIG MANAGEMENT
# ========================
def reset_config(update: Update, context: CallbackContext):
    try:
        user_id = update.effective_user.id
        users[user_id] = UserConfig()
        update.message.reply_text("🔄 Config reset to defaults")
    except Exception as e:
        logger.error(f"Reset error: {e}")

# ========================
# MESSAGE FORWARDING (Safe Handler)
# ========================
def forward_messages(context: CallbackContext):
    try:
        for user_id, config in list(users.items()):
            if config.is_active:
                # Implement your forwarding logic here
                pass
    except Exception as e:
        logger.error(f"Forwarding error: {e}")

# ========================
# BOT SETUP (Railway-Optimized)
# ========================
def main():
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher

        # Add handlers with error logging
        handlers = [
            ('start', start),
            ('work', work),
            ('stop', stop),
            ('blacklist', blacklist),
            ('whitelist', whitelist),
            ('reset_config', reset_config)
        ]
        
        for cmd, handler in handlers:
            dp.add_handler(CommandHandler(cmd, handler))
        
        # Add job queue for forwarding
        job_queue = updater.job_queue
        job_queue.run_repeating(forward_messages, interval=5.0, first=0.0)
        
        logger.info("Bot starting...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.critical(f"Fatal startup error: {e}")

if __name__ == '__main__':
    main()
