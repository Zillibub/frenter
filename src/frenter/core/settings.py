from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: int

    LOOP_TIMEOUT: float = 5


path = Path(__file__).parent.parent.parent.absolute()
settings = Settings(_env_file=path.joinpath(".env"), _env_file_encoding="utf-8")
