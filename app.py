#!/usr/bin/env python3
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        self.token = '7862951291:AAFLCXBgekpq_do1yl63TIFvgtCADjCr66k'
        logger.info("Bot initialized")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bot is running successfully on Render.com!")
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Echo: {update.message.text}")
    
    def run(self):
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
        
        logger.info("Starting bot...")
        app.run_polling()

if __name__ == "__main__":
    try:
        bot = SimpleBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error: {e}")
