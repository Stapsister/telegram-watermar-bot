#!/usr/bin/env python3
import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Bot:
    def __init__(self):
        # Hardcoded token - no environment variable required
        self.token = '7862951291:AAFLCXBgekpq_do1yl63TIFvgtCADjCr66k'
        logger.info("Bot initialized with token")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bot is running successfully on Render.com!")
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Echo: {update.message.text}")
        logger.info(f"Echo message from user {update.effective_user.id}")
    
    async def cleanup_webhook(self):
        """Clean up any existing webhooks before starting polling"""
        try:
            app = Application.builder().token(self.token).build()
            await app.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook cleaned up successfully")
            await app.shutdown()
        except Exception as e:
            logger.warning(f"Webhook cleanup warning: {e}")
    
    def run(self):
        try:
            # Clean up any existing webhooks/conflicts
            asyncio.run(self.cleanup_webhook())
            
            # Wait a moment for cleanup
            import time
            time.sleep(2)
            
            # Start fresh application
            app = Application.builder().token(self.token).build()
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
            
            logger.info("Starting bot polling with conflict resolution...")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                close_loop=False
            )
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

if __name__ == "__main__":
    logger.info("Bot starting with conflict resolution...")
    Bot().run()
