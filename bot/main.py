import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from api_client import get_cars

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привіт! Напиши бюджет, наприклад: 5000 💰")

@dp.message()
async def find_car(message: Message):
    try:
        max_price = int(message.text)

        params = {
            "max_price": max_price
        }

        cars = get_cars(params)

        if not cars:
            await message.answer("❌ Нічого не знайдено")
            return

        result = "🚗 Варіанти:\n\n"

        for car in cars:
            result += (
                f"{car['brand']} {car['model']} {car['mileage']}km \n"
                f"💰 {car['price']}$ | 📅 {car['year']}\n"
                f"{car['reason']}\n\n"
            )
        await message.answer(result)

    except:
        await message.answer("❗ Введи тільки число, наприклад: 5000")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())