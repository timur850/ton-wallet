"""
Бот для TON-кошелька (Mini App). Открывает кошелёк кнопкой и в меню.
Ключи пользователей бот НЕ видит — всё хранится в Mini App на устройстве.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")  # https-ссылка на index.html (например, GitHub Pages)
SUPPORT = os.getenv("SUPPORT", "@Sdelka_ton")

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


def wallet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Открыть кошелёк", web_app=WebAppInfo(url=WEBAPP_URL))],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "💎 Это твой TON-кошелёк прямо в Telegram.\n\n"
        "🔐 Ключи хранятся только на твоём устройстве — даже создатель бота "
        "не имеет доступа к твоим монетам.\n\n"
        "⚠️ Это настоящая сеть TON. Запиши 24 слова на бумагу: без них "
        "восстановить кошелёк невозможно.",
        reply_markup=wallet_kb(),
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "❓ Как пользоваться\n\n"
        "1. Открой кошелёк и нажми «Создать»\n"
        "2. Запиши 24 слова на бумагу — это ключ к деньгам\n"
        "3. Придумай PIN-код\n"
        "4. Нажми «Получить», скопируй адрес и пополни кошелёк\n\n"
        "🔑 Никому не отправляй свои 24 слова — даже поддержке.\n"
        f"Поддержка: {SUPPORT}",
        reply_markup=wallet_kb(),
    )


@dp.message(F.text)
async def any_text(message: Message):
    # если кто-то прислал сид-фразу в чат — предупредим
    if len(message.text.split()) >= 12:
        await message.answer(
            "⚠️ Похоже, ты отправил секретную фразу в чат. Никогда так не делай! "
            "Если это реальный кошелёк — переведи средства на новый."
        )
        return
    await message.answer("Открой кошелёк кнопкой ниже 👇", reply_markup=wallet_kb())


async def main():
    if not WEBAPP_URL or not WEBAPP_URL.startswith("https://"):
        raise SystemExit("Укажи WEBAPP_URL (https://…) в .env")
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text="Кошелёк", web_app=WebAppInfo(url=WEBAPP_URL))
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
