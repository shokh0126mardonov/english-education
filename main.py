import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import telegram dependencies
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Import handlers from handlers package
from handlers import start_handler, handle_contact

# Fetch Telegram Bot token from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        return

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Run the bot
    print("Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

