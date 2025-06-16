#!/usr/bin/env python3
import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Watermark Bot Running')
    
    def log_message(self, format, *args):
        pass

class SimpleWatermarkBot:
    def __init__(self):
        self.token = '7862951291:AAFLCXBgekpq_do1yl63TIFvgtCADjCr66k'
        logger.info("Bot initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """🎨 Professional Watermark Bot

Welcome! I can add watermarks to your photos and videos.

Features:
• High-quality photo watermarking
• Professional video processing  
• Custom text and positioning
• Multiple color options
• Opacity controls

Commands:
/start - Show this message
/help - Usage guide
/settings - Customize watermarks

Send me a photo or video to get started!"""
        
        await update.message.reply_text(welcome_text)
        logger.info(f"Start command for user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """📖 Usage Guide

How to use:
1. Send me a photo or video
2. I'll process it with a watermark
3. Download your branded content

Supported formats:
• Images: JPG, PNG, WebP
• Videos: MP4, MOV (max 100MB)

Features:
• Custom watermark text
• Multiple positions
• Color options
• Opacity control
• Professional quality

Enhanced watermarking features coming soon!

Send your media to start watermarking."""
        
        await update.message.reply_text(help_text)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        settings_text = """⚙️ Settings

Current watermark settings:
• Text: "Sample Watermark"
• Position: Bottom Right
• Color: White
• Opacity: 80%
• Style: Bold

Interactive settings menu coming soon!
For now, send your photos and videos for watermarking.

Use /help for more information."""
        
        await update.message.reply_text(settings_text)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📸 Photo received!\n\n"
            "Professional watermarking features are being upgraded.\n"
            "Your bot is online and ready.\n\n"
            "Enhanced watermarking with interactive menus will be available shortly."
        )
        logger.info(f"Photo received from user {update.effective_user.id}")
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        video = update.message.video
        
        if video and video.file_size > 100 * 1024 * 1024:
            await update.message.reply_text(
                "❌ Video too large!\n\nMaximum size: 100MB\n"
                f"Your video: {round(video.file_size / (1024 * 1024), 1)}MB"
            )
            return
        
        await update.message.reply_text(
            "🎬 Video received!\n\n"
            "Professional watermarking features are being upgraded.\n"
            "Your bot is online and ready.\n\n"
            "Enhanced watermarking with interactive menus will be available shortly."
        )
        logger.info(f"Video received from user {update.effective_user.id}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 Send me a photo or video to watermark!\n\n"
            "Use /help for usage guide\n"
            "Use /settings to see current options"
        )
    
    def start_health_server(self):
        port = int(os.environ.get('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"Health server running on port {port}")
        server.serve_forever()
    
    def run(self):
        try:
            logger.info("Starting Bot...")
            
            health_thread = threading.Thread(target=self.start_health_server, daemon=True)
            health_thread.start()
            
            app = Application.builder().token(self.token).build()
            
            app.add_handler(CommandHandler("start", self.start_command))
            app.add_handler(CommandHandler("help", self.help_command))
            app.add_handler(CommandHandler("settings", self.settings_command))
            
            app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
            app.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
            
            logger.info("Bot polling started")
            app.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Bot startup error: {e}")
            raise

if __name__ == "__main__":
    try:
        bot = SimpleWatermarkBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
