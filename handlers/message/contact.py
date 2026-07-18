from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from django_tenants.utils import schema_context
from app.users.models import Parents
from app.customers.models import Organization

def global_tenant_search(phone_variants: list, telegram_id: int, username: str):
    """Barcha tenantlar ichidan ota-onani qidiradi va DB ga saqlaydi."""
    
    # Public'dan tashqari barcha faol tashkilotlarni olamiz
    tenants = Organization.objects.exclude(schema_name='public')
    
    for tenant in tenants:
        with schema_context(tenant.schema_name):
            parent = Parents.objects.filter(phone__in=phone_variants).first()
            
            if parent:
                parent.telegram_id = telegram_id
                parent.telegram_username = username
                parent.save()
                
                return {
                    "full_name": parent.full_name,
                    "schema_name": tenant.schema_name
                }
    return None

@sync_to_async
def get_and_update_parent_by_phone(phone_number: str, telegram_id: int, username: str) -> dict:
    normalized_phone = "".join(c for c in phone_number if c.isdigit() or c == '+')
    if not normalized_phone.startswith('+'):
        normalized_phone = '+' + normalized_phone

    phone_variants = [normalized_phone]
    if normalized_phone.startswith('+'):
        phone_variants.append(normalized_phone[1:])
        
    # Barcha tenantlar bo'yicha qidiruvni ishga tushiramiz
    return global_tenant_search(phone_variants, telegram_id, username)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle contact messages sent by users."""
    contact = update.message.contact
    
    # Check if the user is sending their own contact
    if contact.user_id != update.message.from_user.id:
        await update.message.reply_text(
            "Iltimos, faqat o'zingizning telefon raqamingizni yuboring."
        )
        return

    phone_number = contact.phone_number
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username or ""

    # Funksiya nomi o'zgarmadi, faqat endi model emas, dict qaytadi
    parent_data = await get_and_update_parent_by_phone(phone_number, telegram_id, username)

    if parent_data:
        await update.message.reply_text(
            f"Muvaffaqiyatli ro'yxatdan o'tdingiz, {parent_data['full_name']}!\n"
            "Endi siz farzandingizning o'zlashtirishi haqidagi ma'lumotlarni qabul qila olasiz."
        )
    else:
        await update.message.reply_text(
            "Kechirasiz, sizning telefon raqamingiz bazadan topilmadi.\n"
            f"Telefon raqamingiz: {phone_number}\n"
            "Iltimos, ma'muriyat bilan bog'lanib, telefon raqamingizni to'g'ri kiritilganini tekshiring."
        )