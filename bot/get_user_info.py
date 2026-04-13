
import json
from dataclasses import asdict, dataclass

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from aiogoogle.sessions.aiohttp_session import AiohttpSession

from bot.env import env_config
from bot.redis import get_redis_client

_creds: ServiceAccountCreds | None = None

_CACHE_KEY = "spreadsheet_cache"


def _get_creds() -> ServiceAccountCreds:
    global _creds
    if _creds is None:
        with open(env_config.creds_path) as f:
            _creds = ServiceAccountCreds(
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
                **json.load(f),
            )
    return _creds


@dataclass
class UserInfo():
    id: str
    username: str
    balance: str
    first_pay: str
    last_pay: str
    tariff: str


def _parse_row(row: list[str]) -> UserInfo:
    return UserInfo(
        id=row[9],
        username=row[0],
        balance=row[5].replace(",", "."),
        first_pay=row[7],
        tariff=row[8].replace(",", "."),
        last_pay=""  # TODO: add to table
    )


async def _get_all_users() -> dict[str, UserInfo]:
    """Return cached {tg_id: UserInfo} dict, fetching from Sheets on miss."""
    redis = get_redis_client()
    try:
        cached = await redis.get(_CACHE_KEY)
        if cached is not None:
            return {
                uid: UserInfo(**data)
                for uid, data in json.loads(cached).items()
            }

        users = await _fetch_all_users()

        await redis.set(
            _CACHE_KEY,
            json.dumps({uid: asdict(info) for uid, info in users.items()}),
            ex=env_config.redis.cache_lifetime,
        )

        return users
    finally:
        await redis.aclose()


async def get_user_info(tg_id: str) -> UserInfo | None:
    users = await _get_all_users()
    return users.get(tg_id)


async def _fetch_all_users() -> dict[str, UserInfo]:
    creds = _get_creds()

    session_factory = AiohttpSession
    if env_config.proxy is not None:
        class ProxiedSession(AiohttpSession):
            async def send(self, *args, **kwargs):
                kwargs["proxy"] = env_config.proxy
                return await super().send(*args, **kwargs)
        session_factory = ProxiedSession

    async with Aiogoogle(service_account_creds=creds, session_factory=session_factory) as g:
        sheets = await g.discover("sheets", "v4")

        clients = await g.as_service_account(
            sheets.spreadsheets.values.get(
                spreadsheetId=env_config.spreadsheet_id,
                range="Расчет!A2:J",
            )
        )

        users: dict[str, UserInfo] = {}
        for row in clients.get("values", []):
            if len(row) >= 10 and row[9]:
                users[row[9]] = _parse_row(row)

        return users
