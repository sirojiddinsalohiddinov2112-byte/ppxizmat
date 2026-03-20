from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "8763489658:AAFAoiuKskqSXBdu855EW0HOf-O3GFcEiD0"
ADMIN_GROUP_ID = -1003589343216  # Bot admin qo‘shilgan guruh ID yoki test uchun shaxsiy user_id

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class OrderState(StatesGroup):
    choosing = State()
    waiting_for_id = State()
    waiting_for_check = State()

# Asosiy menu
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("💰 PP xizmatlari"))

# Narxlar menyusi
pp_prices = InlineKeyboardMarkup(row_width=2)
pp_prices.row(
    InlineKeyboardButton("10K PP - 13K so’m", callback_data="10k"),
    InlineKeyboardButton("20K PP - 26K so’m", callback_data="20k")
)
pp_prices.row(
    InlineKeyboardButton("40K PP - 53K so’m", callback_data="40k"),
    InlineKeyboardButton("50K PP - 65K so’m", callback_data="50k")
)
pp_prices.row(
    InlineKeyboardButton("70K PP - 91K so’m", callback_data="70k"),
    InlineKeyboardButton("100K PP - 130K so’m", callback_data="100k")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Xush kelibsiz!", reply_markup=menu)

@dp.message_handler(lambda message: message.text == "💰 PP xizmatlari")
async def show_prices(message: types.Message):
    message_text = """🤩 Bizda endi POPULYARNOST hizmati bor

• PP Battleda yutishda sizga PP kerak bo’lsa, bizdan PP sotib olishingiz mumkin 

🤑 PP SOTILADIGAN NARXLA:"""
    await message.answer(message_text, reply_markup=pp_prices)
    await OrderState.choosing.set()

@dp.callback_query_handler(state=OrderState.choosing)
async def choose_amount(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(amount=callback.data)
    await bot.send_message(callback.from_user.id, "PUBG ID yuboring:")
    await OrderState.waiting_for_id.set()

@dp.message_handler(state=OrderState.waiting_for_id)
async def get_pubg_id(message: types.Message, state: FSMContext):
    await state.update_data(pubg_id=message.text)
    await message.answer("💳 To‘lov qilingan karta: 8600 1404 2325 0373\n✅ Chek yuboring")
    await OrderState.waiting_for_check.set()

@dp.message_handler(content_types=['photo'], state=OrderState.waiting_for_check)
async def get_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pubg_id = data['pubg_id']
    amount = data['amount']

    caption = f"🆕 Yangi buyurtma\n\nID: {pubg_id}\nUC: {amount}"

    admin_buttons = InlineKeyboardMarkup()
    admin_buttons.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm|{message.from_user.id}"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel|{message.from_user.id}")
    )

    try:
        await bot.send_photo(
            ADMIN_GROUP_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            reply_markup=admin_buttons
        )
        await message.answer("⏳ To‘lov tekshirilmoqda. 2-10 minut kuting.")
    except Exception as e:
        await message.answer(f"❌ Admin guruhiga xabar yuborib bo‘lmadi: {e}")

    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("confirm"))
async def confirm_order(callback: types.CallbackQuery):
    user_id = int(callback.data.split("|")[1])
    await bot.send_message(user_id, "✅ To‘lov qabul qilindi, UC tushadi")
    await callback.answer("Tasdiqlandi")

@dp.callback_query_handler(lambda c: c.data.startswith("cancel"))
async def cancel_order(callback: types.CallbackQuery):
    user_id = int(callback.data.split("|")[1])
    await bot.send_message(user_id, "❌ Buyurtma bekor qilindi")
    await callback.answer("Bekor qilindi")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
