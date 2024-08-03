from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import aiohttp
import os

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

API_URL = "http://web:8000/api/v1"

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Используйте /messages, чтобы получить все сообщения, или /new, чтобы создать новое сообщение.")

@dp.message_handler(commands=['messages'])
async def get_messages(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/messages/") as resp:
            messages = await resp.json()
            response = "\n".join([f"{msg['author']}: {msg['content']}" for msg in messages])
            await message.reply(response, parse_mode=ParseMode.HTML)

@dp.message_handler(commands=['new'])
async def new_message(message: types.Message):
    await message.reply("Пожалуйста, отправьте сообщение в формате: /send [автор] [сообщение]")

@dp.message_handler(commands=['send'])
async def send_message(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.reply("Неверный формат. Используйте /send [автор] [сообщение]")
        return
    author, content = parts[1], parts[2]
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/message/", json={"author": author, "content": content}) as resp:
            if resp.status == 200:
                await message.reply("Сообщение отправлено!")
            else:
                await message.reply("Не удалось отправить сообщение.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
