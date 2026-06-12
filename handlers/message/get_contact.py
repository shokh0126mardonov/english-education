import os
import django

from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import Parents

# 1. Sinxron funksiya: o'zgartirish va saqlash ishlarini bitta joyda qiladi
@sync_to_async(thread_sensitive=True)
def update_parent_telegram_id(parent_obj, telegram_id):
    parent_obj.telegram_id = telegram_id  # Modeldagi maydon nomiga qarab (telegram_id)
    parent_obj.save()

@sync_to_async(thread_sensitive=True)
def check_number(number):
    return Parents.objects.select_related('user').filter(phone=number).first()


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.contact.phone_number

    if not number.startswith('+'):
        number = f"+{number}"

    parent = await check_number(number)

    if parent:
        first_name = parent.user.first_name if parent.user else "Foydalanuvchi"
        
        # DIQQAT: Bu yerda 'await' qo'shildi va qiymat o'zgartirish funksiya ichiga ko'chirildi
        await update_parent_telegram_id(parent, update.effective_user.id)
        
        await update.message.reply_text(
            f"Siz {first_name} ota-onasi sifatida ro'yxatga olindingiz!"
        )
    else:
        await update.message.reply_text(
            "Siz bazadan topilmadingiz!"
        )