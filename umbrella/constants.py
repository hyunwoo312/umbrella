"""
Loads bot configuration from YAML files.
By default, this simply loads the default configuration
located at `config-default.yml` in the root directory.
"""
import os
from typing import Optional

import yaml

MAIN_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(MAIN_DIR, os.pardir))
YAML_FILE_PATH = os.path.join(PROJECT_ROOT, "config-default.yml")

with open(YAML_FILE_PATH, encoding="UTF-8") as config_file:
    CONFIG_YAML = yaml.safe_load(config_file)


class YAMLInitializer(type):
    subsection = None

    def __getattr__(cls, name):
        name = name.lower()

        try:
            if cls.subsection is not None:
                return CONFIG_YAML[cls.section][cls.subsection][name]
            return CONFIG_YAML[cls.section][name]
        except KeyError as e:
            dotted_path = ".".join(
                (cls.section, cls.subsection, name)
                if cls.subsection is not None
                else (cls.section, name)
            )
            print(
                f"Tried accessing configuration variable at `{dotted_path}`, but it could not be found."
            )
            raise AttributeError(repr(name)) from e

    def __getitem__(cls, name):
        return cls.__getattr__(name)

    def __iter__(cls):
        """Return generator of key: value pairs of current constants class' config values."""
        for name in cls.__annotations__:
            yield name, getattr(cls, name)


"""
Loads config values needed to initialize Bot
"""


class BotConfig(metaclass=YAMLInitializer):
    section = "bot"

    prefix: str
    sentry_dsn: Optional[str]
    token: Optional[str]
    trace_loggers: Optional[str]


"""
Loads config values of colors for use
"""


class ColorConfig(metaclass=YAMLInitializer):
    section = "style"
    subsection = "colors"

    aqua: int
    black: int
    blue: int
    green: int
    tomato: int
    white: int
    yellow: int


"""
Loads config values of urls for use
"""


class UrlConfig(metaclass=YAMLInitializer):
    section = "url"

    source: str
