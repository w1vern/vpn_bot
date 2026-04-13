
import os
from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BootLevel(str, Enum):
    DEBUG = "DEBUG"
    RELEASE = "RELEASE"


class RedisSettings(BaseModel):
    model_config = SettingsConfigDict(
        populate_by_name=True)

    ip: str = ""
    port: int = 0
    login: str | None = None
    password: str | None = None
    backend: int = 0
    bot: int = 1
    cache_lifetime: int = 300


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", "dev.env"),
        env_nested_delimiter="_",
        extra="ignore"
    )

    redis: RedisSettings = RedisSettings()
    boot_level: BootLevel = BootLevel.DEBUG
    spreadsheet_id: str = ""
    bot_token: str = ""
    creds_path: str = ""
    proxy: str | None = None

    @field_validator("proxy", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v


env_config = Settings()


if __name__ == "__main__":
    print(env_config.model_dump_json(indent=2))
