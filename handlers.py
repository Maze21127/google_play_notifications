from aiogram import types

from loader import dp



@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message):
    print(message.from_user)
    return await message.answer("I'm working")
