
import asyncio

from bot.bot import start_bot


async def main() -> None:
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
