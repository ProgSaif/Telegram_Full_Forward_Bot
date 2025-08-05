import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('BOT_TOKEN')

def start(update: Update, context):
    update.message.reply_text("🟢 Bot is ONLINE!\nUse /work to start")

def work(update: Update, context):
    update.message.reply_text("✅ Forwarding activated\n/upgrade for premium")

if __name__ == '__main__':
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('start', start))
        dp.add_handler(CommandHandler('work', work))
        
        # Railway-specific health check
        PORT = int(os.getenv('PORT', 8443))
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{os.getenv('RAILWAY_STATIC_URL')}/{BOT_TOKEN}"
        )
        logging.info("Bot successfully deployed on Railway")
        updater.idle()
    except Exception as e:
        logging.error(f"DEPLOY FAILED: {str(e)}")
