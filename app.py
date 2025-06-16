#!/usr/bin/env python3
import logging
import os
import threading
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Watermark Bot Running')
    
    def log_message(self, format, *args):
        pass

class WatermarkBot:
    def __init__(self):
        self.token = '7862951291:AAFLCXBgekpq_do1yl63TIFvgtCADjCr66k'
        self.user_settings = {}
        logger.info("Enhanced Watermark Bot initialized")
    
    def get_default_settings(self):
        return {
            'text': 'Watermark',
            'font_size': 48,
            'opacity': 180,
            'position': 'bottom_right',
            'color': 'white',
            'outline': True,
            'outline_width': 2
        }
    
    def get_user_settings(self, user_id):
        if user_id not in self.user_settings:
            self.user_settings[user_id] = self.get_default_settings()
        return self.user_settings[user_id]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """Professional Watermark Bot

Features:
• High-quality photo watermarking
• Professional video watermarking
• Customizable text, position, colors
• Outline effects for better visibility
• Multiple opacity and size options

Commands:
/start - Welcome message
/settings - Customize watermark
/help - Get detailed help

Send a photo or video to begin watermarking!"""

        await update.message.reply_text(welcome_text)
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """Watermark Bot Help

High-Quality Processing:
• Images: Sharp, clear watermarks
• Videos: Smooth, professional overlay
• Outline effects prevent blur
• Multiple format support

Customization Options:
• Text: Custom watermark text
• Size: Small to Extra Large
• Opacity: 25% to 100%
• Position: 5 placement options
• Colors: 6 color choices
• Outline: Enhanced visibility

Supported Formats:
Images: JPG, PNG, WebP
Videos: MP4, MOV, AVI (under 50MB)

Tips for Best Quality:
• Use outline for better visibility
• Higher opacity for clear text
• Larger fonts for video watermarks"""

        await update.message.reply_text(help_text)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        settings = self.get_user_settings(user_id)
        
        keyboard = [
            [InlineKeyboardButton(f"Text: {settings['text']}", callback_data="set_text")],
            [InlineKeyboardButton(f"Size: {settings['font_size']}", callback_data="set_size"),
             InlineKeyboardButton(f"Opacity: {int(settings['opacity']/255*100)}%", callback_data="set_opacity")],
            [InlineKeyboardButton(f"Position: {settings['position'].replace('_', ' ').title()}", callback_data="set_position")],
            [InlineKeyboardButton(f"Color: {settings['color'].title()}", callback_data="set_color"),
             InlineKeyboardButton(f"Outline: {'On' if settings['outline'] else 'Off'}", callback_data="set_outline")],
            [InlineKeyboardButton("Close", callback_data="close_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings_text = f"""Watermark Settings

Text: {settings['text']}
Size: {settings['font_size']}
Opacity: {int(settings['opacity']/255*100)}%
Position: {settings['position'].replace('_', ' ').title()}
Color: {settings['color'].title()}
Outline: {'Enabled' if settings['outline'] else 'Disabled'}

Click any option to modify:"""
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        context.user_data['pending_photo'] = update.message.photo[-1].file_id
        
        keyboard = [
            [InlineKeyboardButton("Apply Watermark", callback_data="process_photo")],
            [InlineKeyboardButton("Settings", callback_data="show_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings = self.get_user_settings(user_id)
        preview_text = f"""Photo Ready for Processing

Current watermark settings:
Text: {settings['text']}
Size: {settings['font_size']}
Opacity: {int(settings['opacity']/255*100)}%
Position: {settings['position'].replace('_', ' ').title()}

Choose an action:"""
        
        await update.message.reply_text(preview_text, reply_markup=reply_markup)
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.video.file_size > 50 * 1024 * 1024:
            await update.message.reply_text("Video too large! Please send videos under 50MB.")
            return
        
        user_id = str(update.effective_user.id)
        context.user_data['pending_video'] = update.message.video.file_id
        
        keyboard = [
            [InlineKeyboardButton("Apply Watermark", callback_data="process_video")],
            [InlineKeyboardButton("Settings", callback_data="show_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings = self.get_user_settings(user_id)
        preview_text = f"""Video Ready for Processing

Current watermark settings:
Text: {settings['text']}
Size: {settings['font_size']}
Opacity: {int(settings['opacity']/255*100)}%

Choose an action:"""
        
        await update.message.reply_text(preview_text, reply_markup=reply_markup)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        
        if 'updating_text' in context.user_data:
            new_text = update.message.text.strip()
            if len(new_text) > 50:
                await update.message.reply_text("Text too long! Keep under 50 characters.")
                return
            
            settings = self.get_user_settings(user_id)
            settings['text'] = new_text
            del context.user_data['updating_text']
            
            keyboard = [[InlineKeyboardButton("Done", callback_data="text_updated")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(f"Watermark text updated to: '{new_text}'", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Send a photo or video to add watermarks, or use /settings to customize options.")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = str(update.effective_user.id)
        
        if data == "process_photo" and 'pending_photo' in context.user_data:
            await self.process_photo_watermark(update, context, context.user_data['pending_photo'])
        elif data == "process_video" and 'pending_video' in context.user_data:
            await self.process_video_watermark(update, context, context.user_data['pending_video'])
        elif data == "show_settings":
            await self.show_settings_menu(update, context)
        elif data == "set_text":
            context.user_data['updating_text'] = True
            await query.edit_message_text("Send me the new watermark text (max 50 characters):")
        elif data == "set_size":
            await self.show_size_options(update, context)
        elif data == "set_opacity":
            await self.show_opacity_options(update, context)
        elif data == "set_position":
            await self.show_position_options(update, context)
        elif data == "set_color":
            await self.show_color_options(update, context)
        elif data == "set_outline":
            settings = self.get_user_settings(user_id)
            settings['outline'] = not settings['outline']
            status = "enabled" if settings['outline'] else "disabled"
            await query.edit_message_text(f"Outline {status}")
        elif data.startswith("size_"):
            size = int(data.split("_")[1])
            self.get_user_settings(user_id)['font_size'] = size
            await query.edit_message_text(f"Font size set to {size}")
        elif data.startswith("opacity_"):
            opacity_percent = int(data.split("_")[1])
            opacity_value = int(opacity_percent * 255 / 100)
            self.get_user_settings(user_id)['opacity'] = opacity_value
            await query.edit_message_text(f"Opacity set to {opacity_percent}%")
        elif data.startswith("pos_"):
            position = data.replace("pos_", "")
            self.get_user_settings(user_id)['position'] = position
            await query.edit_message_text(f"Position set to {position.replace('_', ' ').title()}")
        elif data.startswith("color_"):
            color = data.split("_")[1]
            self.get_user_settings(user_id)['color'] = color
            await query.edit_message_text(f"Color set to {color.title()}")
        elif data == "close_menu":
            await query.edit_message_text("Settings saved. Send a photo or video to watermark!")
        elif data == "text_updated":
            await query.edit_message_text("Text updated! Send a photo or video to apply the new watermark.")
    
    async def show_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        settings = self.get_user_settings(user_id)
        
        keyboard = [
            [InlineKeyboardButton(f"Text: {settings['text']}", callback_data="set_text")],
            [InlineKeyboardButton(f"Size: {settings['font_size']}", callback_data="set_size"),
             InlineKeyboardButton(f"Opacity: {int(settings['opacity']/255*100)}%", callback_data="set_opacity")],
            [InlineKeyboardButton(f"Position: {settings['position'].replace('_', ' ').title()}", callback_data="set_position")],
            [InlineKeyboardButton(f"Color: {settings['color'].title()}", callback_data="set_color"),
             InlineKeyboardButton(f"Outline: {'On' if settings['outline'] else 'Off'}", callback_data="set_outline")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Watermark Settings\n\nClick any option to change:", reply_markup=reply_markup)
    
    async def show_size_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("Small (32)", callback_data="size_32"), InlineKeyboardButton("Medium (48)", callback_data="size_48")],
            [InlineKeyboardButton("Large (64)", callback_data="size_64"), InlineKeyboardButton("XL (80)", callback_data="size_80")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Choose Font Size:", reply_markup=reply_markup)
    
    async def show_opacity_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("25%", callback_data="opacity_25"), InlineKeyboardButton("50%", callback_data="opacity_50")],
            [InlineKeyboardButton("75%", callback_data="opacity_75"), InlineKeyboardButton("100%", callback_data="opacity_100")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Choose Opacity Level:", reply_markup=reply_markup)
    
    async def show_position_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("Top Left", callback_data="pos_top_left"), InlineKeyboardButton("Top Right", callback_data="pos_top_right")],
            [InlineKeyboardButton("Center", callback_data="pos_center")],
            [InlineKeyboardButton("Bottom Left", callback_data="pos_bottom_left"), InlineKeyboardButton("Bottom Right", callback_data="pos_bottom_right")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Choose Watermark Position:", reply_markup=reply_markup)
    
    async def show_color_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("White", callback_data="color_white"), InlineKeyboardButton("Black", callback_data="color_black")],
            [InlineKeyboardButton("Red", callback_data="color_red"), InlineKeyboardButton("Blue", callback_data="color_blue")],
            [InlineKeyboardButton("Green", callback_data="color_green"), InlineKeyboardButton("Yellow", callback_data="color_yellow")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Choose Watermark Color:", reply_markup=reply_markup)
    
    async def process_photo_watermark(self, update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str):
        await update.callback_query.edit_message_text("Processing photo with high-quality watermark...")
        
        try:
            user_id = str(update.effective_user.id)
            settings = self.get_user_settings(user_id)
            
            file = await context.bot.get_file(file_id)
            photo_bytes = BytesIO()
            await file.download_to_memory(photo_bytes)
            photo_bytes.seek(0)
            
            image = Image.open(photo_bytes).convert('RGBA')
            watermarked_image = self.add_photo_watermark(image, settings)
            
            output_bytes = BytesIO()
            watermarked_image.convert('RGB').save(output_bytes, format='JPEG', quality=95)
            output_bytes.seek(0)
            
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=output_bytes,
                caption=f"Watermarked Photo\n\nText: {settings['text']}\nSize: {settings['font_size']}\nOpacity: {int(settings['opacity']/255*100)}%"
            )
            
            if 'pending_photo' in context.user_data:
                del context.user_data['pending_photo']
            
            logger.info(f"Photo processed successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing photo: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Error processing photo. Please try again with a different image."
            )
    
    async def process_video_watermark(self, update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str):
        await update.callback_query.edit_message_text("Processing video with high-quality watermark... This may take a few minutes.")
        
        try:
            user_id = str(update.effective_user.id)
            settings = self.get_user_settings(user_id)
            
            file = await context.bot.get_file(file_id)
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_input:
                await file.download_to_memory(temp_input)
                input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_output:
                output_path = temp_output.name
            
            success = self.add_video_watermark(input_path, output_path, settings)
            
            if success:
                with open(output_path, 'rb') as video_file:
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=video_file,
                        caption=f"Watermarked Video\n\nText: {settings['text']}\nSize: {settings['font_size']}\nOpacity: {int(settings['opacity']/255*100)}%"
                    )
                
                if 'pending_video' in context.user_data:
                    del context.user_data['pending_video']
                
                logger.info(f"Video processed successfully for user {user_id}")
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text="Error processing video. Please try with a different video file."
                )
            
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Error processing video. Please try again."
            )
    
    def add_photo_watermark(self, image: Image.Image, settings: dict) -> Image.Image:
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", settings['font_size'])
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", settings['font_size'])
            except:
                font = ImageFont.load_default()
        
        text = settings['text']
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x, y = self.calculate_position(image.width, image.height, text_width, text_height, settings['position'])
        
        text_color = self.get_rgba_color(settings['color'], settings['opacity'])
        outline_color = self.get_outline_color(settings['color'])
        
        if settings['outline']:
            outline_width = settings['outline_width']
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill=text_color)
        watermarked = Image.alpha_composite(image, overlay)
        return watermarked
    
    def add_video_watermark(self, input_path: str, output_path: str, settings: dict) -> bool:
        try:
            cap = cv2.VideoCapture(input_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = settings['font_size'] / 40.0
            thickness = max(2, int(font_scale * 3))
            
            text = settings['text']
            (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            
            x, y = self.calculate_position(width, height, text_width, text_height, settings['position'])
            y += text_height
            
            text_color = self.get_bgr_color(settings['color'])
            outline_color = (0, 0, 0) if settings['color'] != 'black' else (255, 255, 255)
            
            alpha = settings['opacity'] / 255.0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                overlay = frame.copy()
                
                if settings['outline']:
                    outline_thickness = thickness + settings['outline_width']
                    cv2.putText(overlay, text, (x, y), font, font_scale, outline_color, outline_thickness)
                
                cv2.putText(overlay, text, (x, y), font, font_scale, text_color, thickness)
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
                out.write(frame)
            
            cap.release()
            out.release()
            return True
            
        except Exception as e:
            logger.error(f"Video watermarking error: {e}")
            return False
    
    def calculate_position(self, width: int, height: int, text_width: int, text_height: int, position: str) -> tuple:
        margin = 30
        
        positions = {
            'top_left': (margin, margin),
            'top_right': (width - text_width - margin, margin),
            'center': ((width - text_width) // 2, (height - text_height) // 2),
            'bottom_left': (margin, height - text_height - margin),
            'bottom_right': (width - text_width - margin, height - text_height - margin)
        }
        
        return positions.get(position, positions['bottom_right'])
    
    def get_rgba_color(self, color_name: str, opacity: int) -> tuple:
        colors = {
            'white': (255, 255, 255, opacity),
            'black': (0, 0, 0, opacity),
            'red': (255, 0, 0, opacity),
            'green': (0, 255, 0, opacity),
            'blue': (0, 0, 255, opacity),
            'yellow': (255, 255, 0, opacity)
        }
        return colors.get(color_name.lower(), (255, 255, 255, opacity))
    
    def get_bgr_color(self, color_name: str) -> tuple:
        colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255)
        }
        return colors.get(color_name.lower(), (255, 255, 255))
    
    def get_outline_color(self, color_name: str) -> tuple:
        if color_name.lower() in ['white', 'yellow']:
            return (0, 0, 0, 255)
        else:
            return (255, 255, 255, 255)
    
    def start_health_server(self):
        port = int(os.environ.get('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"Health server running on port {port}")
        server.serve_forever()
    
    def run(self):
        health_thread = threading.Thread(target=self.start_health_server, daemon=True)
        health_thread.start()
        
        app = Application.builder().token(self.token).build()
        
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("settings", self.settings_command))
        app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        app.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("Enhanced Watermark Bot starting...")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        bot = WatermarkBot()
        bot.run()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
