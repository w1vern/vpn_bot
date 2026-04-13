
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", "dev.env"),
        env_nested_delimiter="_",
        extra="ignore"
    )

    spreadsheet_id: str = ""
    bot_token: str = ""
    creds_path: str = ""
    proxy: str = ""


env_config = Settings()


if __name__ == "__main__":
    print(env_config.model_dump_json(indent=2))
