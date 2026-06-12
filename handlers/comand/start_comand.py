from telegram import Update
from telegram.ext import ContextTypes
from telegram import ReplyKeyboardMarkup,KeyboardButton

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"Assalomu alekum {update.effective_user.full_name}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton('Contact',request_contact=True)]
            ],one_time_keyboard=True,resize_keyboard=True
        )
    )