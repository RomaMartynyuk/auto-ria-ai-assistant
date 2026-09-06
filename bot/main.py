import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from bot.api_client import get_cars

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required to run the Telegram bot")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
POLL_ATTEMPTS = int(os.getenv("BOT_POLL_ATTEMPTS", "6"))
POLL_INTERVAL = float(os.getenv("BOT_POLL_INTERVAL", "3"))

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привіт! Напиши бюджет у доларах, наприклад: 15000")


async def wait_for_recommendations(max_price):
    for attempt in range(POLL_ATTEMPTS):
        result = await get_cars({"max_price": max_price})
        if result.get("status") != "processing":
            return result
        if attempt < POLL_ATTEMPTS - 1:
            await asyncio.sleep(POLL_INTERVAL)

    return {
        "status": "processing",
        "message": "Пошук займає трохи довше. Спробуй повторити запит за хвилину.",
    }

@dp.message()
async def find_car(message: Message):
    try:
        max_price = int(message.text)
        if max_price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        await message.answer("Введи додатне число, наприклад: 15000")
        return

    await message.answer("Шукаю актуальні варіанти, це може зайняти кілька секунд...")
    result = await wait_for_recommendations(max_price)

    if result.get("status") == "processing":
        await message.answer(result["message"])
        return

    if result.get("status") == "error":
        logger.error("Car API error: %s", result.get("message"))
        await message.answer("Сервіс тимчасово недоступний. Спробуй трохи пізніше.")
        return

    cars = result.get("cars", [])
    if not cars:
        await message.answer("Не знайшов варіантів у цьому бюджеті.")
        return

    lines = ["Варіанти:", ""]
    for car in cars:
        lines.extend(
            [
                f"{car['brand']} {car['model']} ({car['year']})",
                f"Ціна: ${car['price']} | Пробіг: {car['mileage']} км",
                car.get("reason", ""),
                car.get("link", ""),
                "",
            ]
        )

    await message.answer("\n".join(line for line in lines if line is not None))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
