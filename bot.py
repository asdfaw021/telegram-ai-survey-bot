import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()

API_TOKEN = os.getenv("API_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который будет создавать опросы!")


@dp.message(Command("Hi"))
async def send_hi(message: types.Message):
    await message.reply("Привет! Ну и лол")


@dp.message(Command("poll"))
async def send_poll(message: types.Message):
    question = "Какой твой любимый язык программирования?"
    options = ["Python", "C++", "Java", "Rust"]
    await bot.send_poll(
        chat_id=message.chat.id,
        question=question,
        options=options,
        is_anonymous=True
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
