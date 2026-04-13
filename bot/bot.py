
from aiogram import Bot, Dispatcher, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.types import BotCommand, Message

from bot.env import env_config
from bot.get_user_info import get_user_info

session = AiohttpSession(proxy=env_config.proxy)

router = Router()


@router.message(Command("info"))
async def info_handler(message: Message) -> None:
    if message.from_user is None:
        return
    user_info = await get_user_info(str(message.from_user.id))
    if user_info is None:
        await message.answer("Твоего id нет в базе")
        return
    await message.answer(f"Твой баланс: {user_info.balance // 100}.{user_info.balance % 100} ₽\nТариф: {user_info.tariff} ₽ в месяц")


async def start_bot() -> None:
    bot = Bot(
        token=env_config.bot_token,
        session=session
    )
    await bot.set_my_commands([
        BotCommand(command="info", description="Мой баланс"),
    ])
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
