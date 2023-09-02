"""
Loads bot configuration from environment variables and `.env` files.

By default, the values defined in the classes are used,

which could be overridden with an env var with the same naem.
"""
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

MAIN_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(MAIN_DIR, os.pardir))

PING_USER_ID = lambda user_id: f"<@!{user_id}>"


class BaseConfig(BaseSettings):
    """
    Default base configuration for the constant models.
    """

    model_config = SettingsConfigDict(
        env_file=(".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class _BotConfig(BaseConfig):
    """
    Default config values needed to initialize Bot.
    """

    discord_app_id: str  # Loaded from '.env' file
    discord_token: str  # Loaded from '.env' file
    prefix: str = "!"


BotConfig = _BotConfig()


class _ColorConfig(BaseConfig):
    """
    Default config values of colors for use.
    """

    aqua: int = 0x00FFFF
    azure: int = 0xF0FFFF
    black: int = 0x000000
    blue: int = 0x0000FF
    green: int = 0x008000
    mintcream: int = 0xF5FFFA
    orange: int = 0xFFA500
    palegreen: int = 0x98FB98
    peachpuff: int = 0xFFDAB9
    tomato: int = 0xFF6347
    white: int = 0xFFFFFF
    yellow: int = 0xFFFF00


ColorConfig = _ColorConfig()


class _LogConfig(BaseConfig):
    """
    Default config values for logging.
    """

    debug: bool = True
    file_logs: bool = True
    trace_level: int = 5

    backup_count: int = 5
    encoding: str = "utf-8"
    max_bytes: int = 8 * 1024 * 1024 * 4  # 4 MB
    string_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


LogConfig = _LogConfig()


class _TimeConfig(BaseConfig):
    """
    Default config values for datetime related values.
    """

    datetime_format_full: str = "%Y-%m-%d %H:%M:%S"
    datetime_format_ymd: str = "%Y-%m-%d"
    datetime_format_hms: str = "%H:%M:%S"


TimeConfig = _TimeConfig()


class _UrlConfig(BaseConfig):
    """
    Default config values of urls for use.
    """

    source: str = "https://github.com/hyunwoo312/umbrella"


UrlConfig = _UrlConfig()
