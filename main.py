import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# In-memory storage (persists until bot restart)
users = {}

class UserConfig:
    def __init__(self):
        self.sources = []
        self.targets = []
        self.is_premium = False
        self.last_work = None

# Command Handlers
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    users[user_id] = UserConfig()
    
    update.message.reply_text(
        "🔄 Auto Message Forwarder Bot\n\n"
        "Use /work to start forwarding\n"
        "Manually send /work again to restart\n\n"
        "Premium users get uninterrupted service\n"
        "/upgrade for premium benefits!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌟 Upgrade", callback_data='upgrade')],
            [InlineKeyboardButton("⚙️ Config", callback_data='config')]
        ])
    )

def work(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.get(user_id, UserConfig())
    
    update.message.reply_text(
        "✅ Forwarding STARTED\n"
        f"Sources: {len(user.sources)} | Targets: {len(user.targets)}\n\n"
        "⚠️ Free service stops after 30 mins\n"
        "/upgrade for uninterrupted forwarding"
    )

def upgrade(update: Update, context: CallbackContext):
    users[update.effective_user.id].is_premium = True
    update.message.reply_text("💎 Premium Activated!")

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'upgrade':
        upgrade(update, context)
    elif query.data == 'config':
        config(update, context)

def config(update: Update, context: CallbackContext):
    user = users.get(update.effective_user.id, UserConfig())
    update.message.reply_text(
        f"⚙️ Your Config:\n"
        f"Sources: {len(user.sources)}\n"
        f"Targets: {len(user.targets)}\n"
        f"Status: {'PREMIUM 💎' if user.is_premium else 'FREE 🆓'}"
    )

if __name__ == '__main__':
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        
        # Command handlers
        dp.add_handler(CommandHandler('start', start))
        dp.add_handler(CommandHandler('work', work))
        dp.add_handler(CommandHandler('upgrade', upgrade))
        dp.add_handler(CommandHandler('config', config))
        
        # Button handler
        dp.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("Bot starting...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
