from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    contact_keyboard = KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)
    custom_keyboard = [[contact_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "Assalomu alaykum! Ota-onalar tizimiga xush kelibsiz.\n"
        "Tizimda ro'yxatdan o'tganingizni tasdiqlash uchun, iltimos, pastdagi 'Telefon raqamni yuborish' tugmasini bosing.",
        reply_markup=reply_markup,
    )
