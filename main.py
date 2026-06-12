from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler,MessageHandler,filters

from decouple import config
from handlers import start,contact


def main() -> None:
    application = Application.builder().token(config("TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT,contact))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()