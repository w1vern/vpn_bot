
import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import BotCommand, ErrorEvent, Message

from bot.env import env_config
from bot.get_user_info import get_user_info
from bot.i18n import LANGUAGES, t
from bot.logger import setup_logger

logger = setup_logger(__name__)

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    if message.from_user is None:
        return
    lang = message.from_user.language_code
    await message.answer(t("start", lang), parse_mode=ParseMode.HTML)


@router.message(Command("info"))
async def info_handler(message: Message) -> None:
    if message.from_user is None:
        return
    lang = message.from_user.language_code
    user_info = await get_user_info(str(message.from_user.id))
    if user_info is None:
        await message.answer(t("info.not_found", lang), parse_mode=ParseMode.HTML)
        return
    await message.answer(
        t("info.result", lang, balance=user_info.balance, tariff=user_info.tariff),
        parse_mode=ParseMode.HTML,
    )


@router.message()
async def unknown_handler(message: Message) -> None:
    if message.from_user is None:
        lang = None
    else:
        lang = message.from_user.language_code
    await message.answer(t("unknown", lang), parse_mode=ParseMode.HTML)


@router.error()
async def error_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled error: %s", event.exception)
    message = event.update.message
    if message is not None and message.from_user is not None:
        lang = message.from_user.language_code
        await message.answer(t("error", lang), parse_mode=ParseMode.HTML)
    return True


async def start_bot() -> None:
    retry_delay = 5
    max_retry_delay = 60

    while True:
        session = AiohttpSession(proxy=env_config.proxy) if env_config.proxy else AiohttpSession()
        try:
            bot = Bot(
                token=env_config.bot_token,
                session=session,
            )
            commands = [BotCommand(command="info", description=t("cmd.info", None))]
            await bot.set_my_commands(commands)
            for lang in LANGUAGES:
                await bot.set_my_commands(
                    [BotCommand(command="info", description=t("cmd.info", lang))],
                    language_code=lang,
                )
            dp = Dispatcher()
            dp.include_router(router)
            retry_delay = 5
            await dp.start_polling(bot)
            break
        except Exception as e:
            logger.error("Polling stopped with error: %s. Retrying in %ds...", e, retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_retry_delay)
        finally:
            await session.close()
