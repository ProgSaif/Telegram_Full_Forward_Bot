import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv('BOT_TOKEN')

# In-memory storage (persists until bot restarts)
users = {}
forwarding_active = {}

class UserConfig:
    def __init__(self):
        self.sources = []
        self.targets = []
        self.filters = {}
        self.is_premium = False
        self.last_work = None

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in users:
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
    
    # Free user cooldown check
    if not user.is_premium and user.last_work and (datetime.now() - user.last_work) < timedelta(minutes=30):
        update.message.reply_text("⏳ Free users must wait 30 mins between /work commands")
        return
    
    user.last_work = datetime.now()
    forwarding_active[user_id] = True
    update.message.reply_text(
        "✅ Forwarding STARTED\n"
        f"Sources: {len(user.sources)} | Targets: {len(user.targets)}\n\n"
        "⚠️ Free service stops after 30 mins\n"
        "/upgrade for uninterrupted forwarding",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛑 Stop", callback_data='stop')]
        ])
    )

def upgrade(update: Update, context: CallbackContext):
    users[update.effective_user.id].is_premium = True
    update.message.reply_text(
        "💎 Premium Activated!\n"
        "Now enjoy:\n"
        "- No /work cooldowns\n"
        "- 24/7 forwarding\n"
        "- Priority support"
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'upgrade':
        upgrade(update, context)
    elif query.data == 'config':
        config(update, context)
    elif query.data == 'stop':
        forwarding_active.pop(update.effective_user.id, None)
        query.edit_message_text("🛑 Forwarding STOPPED")

def config(update: Update, context: CallbackContext):
    user = users.get(update.effective_user.id, UserConfig())
    status = "🟢 ACTIVE" if forwarding_active.get(update.effective_user.id) else "🔴 INACTIVE"
    
    update.message.reply_text(
        f"⚙️ Your Config:\n"
        f"Status: {status}\n"
        f"Sources: {len(user.sources)}\n"
        f"Targets: {len(user.targets)}\n"
        f"Tier: {'PREMIUM 💎' if user.is_premium else 'FREE 🆓'}\n\n"
        "/incoming - Setup sources\n"
        "/outgoing - Setup targets\n"
        "/filter - Add text filters"
    )

if __name__ == '__main__':
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('work', work))
    dp.add_handler(CommandHandler('upgrade', upgrade))
    dp.add_handler(CommandHandler('config', config))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot running on Railway!")
    updater.start_polling()
    updater.idle()
