import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from openai import OpenAI

API_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
client = OpenAI(api_key=OPENAI_KEY)

PRODUCTS = {
    "qiyma": 12000,
    "jaz": 17000,
    "ko'mir": 25000,
}

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: Message):
    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path
    downloaded = await bot.download_file(file_path)

    with open("voice.ogg", "wb") as f:
        f.write(downloaded.read())

    audio_file = open("voice.ogg", "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    text = transcript.text.lower()

    total = 0
    result_text = "🧾 Yangi sotuv:\n\n"

    for product, price in PRODUCTS.items():
        if product in text:
            import re
            numbers = re.findall(r"\d+", text)
            if numbers:
                qty = int(numbers[0])
                subtotal = qty * price
                total += subtotal
                result_text += f"{product.title()} — {qty} ta × {price} = {subtotal}\n"

    result_text += f"\n💰 Jami: {total} so'm"

    await bot.send_message(ADMIN_ID, result_text)
    await bot.send_voice(ADMIN_ID, message.voice.file_id)

if __name__ == "__main__":
    executor.start_polling(dp)
