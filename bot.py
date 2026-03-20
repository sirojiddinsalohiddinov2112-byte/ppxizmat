from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_GROUP_ID = -100123456789

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class OrderState(StatesGroup):
    choosing = State()
    waiting_for_id = State()
    waiting_for_check = State()

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("💰 PP xizmatlari"))

prices = InlineKeyboardMarkup()
prices.add(
    InlineKeyboardButton("60 UC - 10k", callback_data="60"),
    InlineKeyboardButton("325 UC - 50k", callback_data="325")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Xush kelibsiz!", reply_markup=menu)

@dp.message_handler(lambda message: message.text == "💰 PP xizmatlari")
async def show_prices(message: types.Message):
    await message.answer("Narxni tanlang:", reply_markup=prices)
    await OrderState.choosing.set()

@dp.callback_query_handler(state=OrderState.choosing)
async def choose_amount(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(amount=callback.data)
    await bot.send_message(callback.from_user.id, "PUBG ID yuboring:")
    await OrderState.waiting_for_id.set()

@dp.message_handler(state=OrderState.waiting_for_id)
async def get_pubg_id(message: types.Message, state: FSMContext):
    await state.update_data(pubg_id=message.text)
    await message.answer("💳 To‘lov karta:
8600 XXXX XXXX XXXX

Chek yuboring:")
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

    await bot.send_photo(
        ADMIN_GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        reply_markup=admin_buttons
    )

    await message.answer("⏳ To‘lov tekshirilmoqda. 2-10 minut kuting.")
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
