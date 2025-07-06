import asyncio
import os
import requests
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()

BOT_API_TOKEN = os.getenv("BOT_API_KEY")
YANDEX_API_TOKEN = os.getenv("YANDEX_API_TOKEN")
YANDEX_CATALOG_ID = os.getenv("YANDEX_CATALOG_ID")

model_uri = f"gpt://{YANDEX_CATALOG_ID}/yandexgpt-lite"
yandex_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {YANDEX_API_TOKEN}"
}

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher()


def generate_poll_content():
    prompt = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты ассистент, который генерирует вопросы и варианты ответов для опросов."
                        "Формат ответа: \nВопрос: [вопрос]\n1. [вариант1]\n2. [вариант2]\n3. [вариант3]\n4. [вариант4]"
            },
            {
                "role": "user",
                "text": "Сгенерируй вопрос и 4 варианта ответа для опроса в тг."
            }
        ]
    }
    response = requests.post(yandex_url, headers=HEADERS, json=prompt)
    response.raise_for_status()
    result = response.json()
    return result['result']['alternatives'][0]['message']['text']


def parse_poll_content(text):
    try:
        lines = text.strip().split('\n')
        question_match = re.match(r'Вопрос:\s*(.+)', lines[0])
        if not question_match:
            raise ValueError("Вопрос не найден в ответе YandexGPT")
        question = question_match.group(1)

        options = []
        for line in lines[1:]:
            option_match = re.match(r'\d+\.\s*(.+)', line)
            if option_match:
                options.append(option_match.group(1))

        if len(options) < 2:
            raise ValueError("Недостаточно вариантов ответа (нужно минимум 2)")
        return question, options
    except Exception as e:
        raise ValueError(f"Ошибка при парсинге ответа YandexGPT: {e}")


@dp.message(Command("yapoll"))
async def send_yandex_poll(message: types.Message):
    try:
        poll_text = generate_poll_content()
        question, options = parse_poll_content(poll_text)
        await bot.send_poll(
            chat_id=message.chat.id,
            question=question,
            options=options[:10],
            is_anonymous=True,
            type="regular"
        )
    except Exception as e:
        await message.reply(f"Что-то пошло не так: {str(e)}")


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот генерирующий опросы!\nОтправь мне /yapoll для опроса!")


@dp.message(Command("dice"))
async def send_dice(message: types.Message):
    await message.reply_dice(emoji="🎲")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
