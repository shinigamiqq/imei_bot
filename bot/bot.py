import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
import requests
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('TOKEN')  # Токен вашего бота
bot = Bot(
    token=API_TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

router = Router()

def load_whitelist(file_path):
    try:
        with open(file_path, "r") as file:
            return [int(line.strip()) for line in file if line.strip().isdigit()]
    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден. Создайте файл с белым списком.")
        return []
    except ValueError:
        logging.error(f"Некорректные данные в файле {file_path}. Проверьте содержимое.")
        return []

WHITELIST = load_whitelist("bot/whitelist.txt")

def check_imei(imei, token):
    url = f"http://api:8000/api/check-imei/imei={imei}&token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    if message.from_user.id not in WHITELIST:
        await message.reply("Доступ запрещен.")
        return
    await message.reply(
            "Привет! Отправь мне IMEI и токен для проверки.\n"
            "Формат: <code>/check IMEI TOKEN</code>",
            parse_mode="HTML"
    )

@router.message(Command("check"))
async def check_imei_command(message: types.Message):
    if message.from_user.id not in WHITELIST:
        await message.reply("Доступ запрещен.")
        return

    args = message.text.split()[1:]
    if len(args) != 2:
        await message.reply(
            "Привет! Отправь мне IMEI и токен для проверки.\n"
            "Формат: <code>/check IMEI TOKEN</code>",
            parse_mode="HTML"
        )
        return

    imei, token = args

    if not imei.isdigit() or len(imei) != 15:
        await message.reply("Некорректный IMEI. IMEI должен состоять из 15 цифр.")
        return

    data = check_imei(imei, token)
    if data:
        response_text = ""
        for item in data:
            properties = item.get('properties', {})
            response_text += f"Устройство: {properties.get('deviceName', 'Неизвестно')}\n"
            response_text += f"IMEI: {properties.get('imei', 'Неизвестно')}\n"
            response_text += f"Серийный номер: {properties.get('serial', 'Неизвестно')}\n"
            response_text += f"Статус блокировки: {properties.get('gsmaBlacklisted', 'Неизвестно')}\n"
            response_text += f"Сеть: {properties.get('network', 'Неизвестно')}\n"
            response_text += f"Регион: {properties.get('apple/region', 'Неизвестно')}\n"
            response_text += f"Статус гарантии: {properties.get('warrantyStatus', 'Неизвестно')}\n"
            response_text += f"Режим пропажи: {properties.get('lostMode', 'Неизвестно')}\n"
            response_text += f"Статус блокировки в США: {properties.get('usaBlockStatus', 'Неизвестно')}\n"
            response_text += "\n"
        await message.reply(response_text)
    else:
        await message.reply("Не удалось получить информацию по IMEI. Проверьте токен и IMEI.")

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

