import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from google import genai

# =====================================================================
# 🔑 TOKEN VA SOZLAMALAR (KODNING ENG TEPASIDA)
# =====================================================================
BOT_TOKEN = "8555501611:AAGBNNBOLgXWd95aDTfxMpSE0FJB4znnfXc"  # BotFather'dan olgan tokeningizni qo'ying
GEMINI_API_KEY = "03ab056d00a2938be95bf5daa312afe7"  # Google AI Studio'dan olgan kalitingizni qo'ying
ADMIN_ID = 8289361035                         # 👈 @userinfobot'dan olgan shaxsiy ID raqamingizni shu yerga yozing (qo'shtirnoqsiz!)
ADMIN_USERNAME = "@Abdulazizzz"            # Mijozlar ko'radigan profilingiz usernami

# Logging (Konsolda bot harakatlarini kuzatish uchun)
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# AI (Gemini) mijozini ishga tushiramiz
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# =====================================================================
# 📝 RO'YXATDAN O'TISH HOLATLARI (FSM)
# =====================================================================
class RegisterState(StatesGroup):
    waiting_for_name = State()      # Ismini kutish holati
    waiting_for_phone = State()     # Telefon raqamini kutish holati
    waiting_for_address = State()   # Manzilini kutish holati

# =====================================================================
# ⌨️ KLAVIATURALAR (Tugmalar)
# =====================================================================
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="👕 Tovar (Katalog)")
    builder.button(text="📝 Ro'yxatdan o'tish (Register)")
    builder.button(text="📞 Biz bilan bog'lanish")
    builder.adjust(2)  # Tugmalarni chiroyli 2 qator qiladi
    return builder.as_markup(resize_keyboard=True)

def get_phone_keyboard():
    builder = ReplyKeyboardBuilder()
    # Raqamni bitta bosishda yuborish tugmasi
    builder.button(text="📱 Telefon raqamni yuborish", request_contact=True)
    return builder.as_markup(resize_keyboard=True)

def get_products_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 SILENCE. Oversize Futbolka", callback_data="prod_tshirt")
    builder.button(text="📦 SILENCE. Aesthetic Hoodie", callback_data="prod_hoodie")
    builder.adjust(1)
    return builder.as_markup()

# =====================================================================
# 🚀 BOT BUYRUKLARI VA ASOSIY TUGMALAR
# =====================================================================

# /start buyrug'i kelganda
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    # Har safar start bosilganda eski qolib ketgan holatlarni tozalaydi
    await state.clear()
    welcome_text = (
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        f"**SILENCE.** brendining rasmiy botiga xush kelibsiz.\n\n"
        f"Xarid qilishni boshlash uchun iltimos **📝 Ro'yxatdan o'tish (Register)** tugmasini bosing yoki o'zingizni qiziqtirgan savolni srazi shu yerga yozing!"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# "Biz bilan bog'lanish" tugmasi bosilganda
@dp.message(F.text == "📞 Biz bilan bog'lanish")
async def contact_us(message: types.Message):
    contact_text = (
        f"👋 **SILENCE. jamoasi bilan bog'lanish**\n\n"
        f"Savollar yoki takliflar bo'yicha loyiha rahbariga to'g'ridan-to'g'ri yozishingiz mumkin:\n"
        f"➡️ Administrator: {ADMIN_USERNAME}\n\n"
        f"Ish vaqti: 09:00 dan 22:00 gacha."
    )
    await message.answer(contact_text, parse_mode="Markdown")

# "Tovar (Katalog)" tugmasi bosilganda
@dp.message(F.text == "👕 Tovar (Katalog)")
async def show_products(message: types.Message):
    await message.answer("Hozirda mavjud bo'lgan eksklyuziv kiyimlarimiz:", reply_markup=get_products_keyboard())

# Tovar tugmalari bosilganda (Inline callback)
@dp.callback_query(F.data.startswith("prod_"))
async def product_detail(callback: types.CallbackQuery):
    if callback.data == "prod_tshirt":
        text = (
            "👕 **SILENCE. Premium Oversize Futbolka**\n\n"
            "• **Mato:** 100% Paxta (240g Heavyweight)\n"
            "• **Orqa qismi:** Oltin-qumrang tog' grafikasi va\n"
            "«Искусство быть собой в мире, где все хотят быть кем-то другим» sitatasi.\n\n"
            "💰 Narxi: 220 000 so'm"
        )
        await callback.message.answer(text, parse_mode="Markdown")
    elif callback.data == "prod_hoodie":
        text = (
            "🥼 **SILENCE. Aesthetic Hoodie (Hudi)**\n\n"
            "• **Mato:** Uch iplik futra (Nachosli/Fleece, qalin issiq mato)\n"
            "• **Dizayn:** Elegant tog' pechati va eksklyuziv yozuvlar.\n\n"
            "💰 Narxi: 390 000 so'm"
        )
        await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

# =====================================================================
# 🛠️ RO'YXATDAN O'TISH TIZIMI (REGISTER LOGIKA)
# =====================================================================

# 1-Qadam: Register tugmasi bosilganda
@dp.message(F.text == "📝 Ro'yxatdan o'tish (Register)")
async def start_register(message: types.Message, state: FSMContext):
    await message.answer("Keling, ro'yxatdan o'tamiz! Ism va familiyangizni kiriting:")
    await state.set_state(RegisterState.waiting_for_name)

# 2-Qadam: Ism kiritilganda
@dp.message(RegisterState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Rahmat! Endi pastdagi tugmani bosish orqali telefon raqamingizni yuboring:",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegisterState.waiting_for_phone)

# 3-Qadam: Telefon raqam yuborilganda
@dp.message(RegisterState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)
    await message.answer(
        "Ajoyib! Oxirgi qadam: kiyimlarni yetkazib berish uchun to'liq manzilingizni kiriting:",
        reply_markup=types.ReplyKeyboardRemove() # Raqam tugmasini vaqtincha olib tashlaydi
    )
    await state.set_state(RegisterState.waiting_for_address)

# 4-Qadam: Manzil kiritilganda (Yakunlash va srazi adminga lichkaga tashlash)
@dp.message(RegisterState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    user_data = await state.get_data()

    # Foydalanuvchiga chiqadigan xabar
    summary_text = (
        "🎉 **Ro'yxatdan muvaffaqiyatli o'tdingiz!**\n\n"
        "Siz kiritgan ma'lumotlar:\n"
        "👤 **Ism:** {}\n"
        "📱 **Telefon:** {}\n"
        "📍 **Manzil:** {}\n\n"
        "Ma'lumotlaringiz qabul qilindi. Operatorimiz tez orada bog'lanadi!".format(
            user_data['name'], user_data['phone'], user_data['address']
        )
    )
    await message.answer(summary_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

    # 🚨 SIZNING LICHKANGIZGA (ADMINGA) BORADIGAN BUYURTMA XABARI 🚨
    admin_text = (
        "🔔 **YANGI KLIYENT RO'YXATDAN O'TDI!**\n\n"
        "Mijoz ma'lumotlari:\n"
        "👤 **Ismi:** {}\n"
        "📱 **Telefoni:** {}\n"
        "📍 **Manzili:** {}\n\n"
        "🔗 **Telegram profili:** [Profilga o'tish](tg://user?id={})\n"
        "👤 **Username:** @{}".format(
            user_data['name'],
            user_data['phone'],
            user_data['address'],
            message.from_user.id,
            message.from_user.username if message.from_user.username else "Mavjud emas"
        )
    )

    try:
        # Bot sizning lichkangizga xabarni jo'natadi
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Adminga xabar yuborishda xatolik: {e}")

    # Holatni tozalaymiz, bot yana oddiy rejimga qaytadi
    await state.clear()

# =====================================================================
# 🧠 AI YORDAMCHI (Har qanday savolga aqlli javob berish)
# =====================================================================
@dp.message()
async def ai_chat_handler(message: types.Message):
    user_prompt = message.text
    system_instruction = (
        "Sen SILENCE. nomli zamonaviy, elegant yoshlar kiyim brendining aqlli virtual yordamchisisan. "
        "Mijozlarning har qanday savollariga chiroyli va tushunarli o'zbek tilida javob ber."
    )

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config={'system_instruction': system_instruction}
        )
        await message.answer(response.text)
    except Exception as e:
        logging.error(f"AI xatolik: {e}")
        await message.answer("Uzr, savolingizni qayta ishlashda xatolik yuz berdi.")

# =====================================================================
# 🏁 BOTNI ISHGA TUSHIRISH
# =====================================================================
async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
