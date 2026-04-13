
import json
from dataclasses import dataclass

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

from bot.env import env_config

creds = ServiceAccountCreds(
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    **json.load(open(env_config.creds_path))
)


@dataclass
class UserInfo():
    id: str
    username: str
    balance: int
    first_pay: str
    last_pay: str
    tariff: int


async def get_user_info(tg_id: str) -> UserInfo | None:
    async with Aiogoogle(service_account_creds=creds) as g:
        sheets = await g.discover("sheets", "v4")

        clients = await g.as_service_account(
            sheets.spreadsheets.values.get(
                spreadsheetId=env_config.spreadsheet_id,
                range="Расчет!A2:J"
            )
        )

        username = None
        for row in clients.get("values", []):
            if len(row) >= 10 and row[9] == tg_id:
                return UserInfo(
                    id=row[9],
                    username=row[0],
                    balance=-int(row[5].replace(",", "")),
                    first_pay=row[7],
                    tariff=int(row[8]),
                    last_pay=""  # TODO: add to table
                )

        return None
