#!/usr/bin/env python3
import os
import logging
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
        logger.info("Bot initialized successfully")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Bot is running successfully on Render.com!")
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Echo: {update.message.text}")
        logger.info(f"Echo message from user {update.effective_user.id}")
    
    def run(self):
        try:
            logger.info("Creating Telegram application...")
            app = Application.builder().token(self.token).build()
            
            # Add handlers
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
            
            logger.info("Starting bot polling...")
            
            # Simple polling without asyncio complications
            app.run_polling(
                poll_interval=1.0,
                timeout=10,
                bootstrap_retries=5,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
                pool_timeout=30,
                drop_pending_updates=True
            )
            
        except Exception as e:
