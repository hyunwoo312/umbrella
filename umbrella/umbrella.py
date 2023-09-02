import asyncio

from discord.ext import commands

from umbrella import exts
from umbrella.log import get_logger
from umbrella.utils.extensions import get_module_names


class Umbrella(commands.Bot):
    """A subclass of `discord.ext.commands.Bot` that implements other functions."""

    LOADING_SUCCESS_MESSAGE = (
        lambda name, cogs: f"All {name} successfully loaded: {list(cogs)}"
    )

    def __init__(self, *args, **kwargs):
        """Initialize the bot instance `Umbrella`."""
        super().__init__(*args, **kwargs)

        self.logger = get_logger()

    async def setup_hook(self) -> None:
        """Custom `setup_hook()` method that also loads extensions on `Umbrella`."""
        await super().setup_hook()

        background_tasks = set()
        cog_modules = get_module_names(exts)

        for cog in cog_modules:
            task = asyncio.create_task(self.load_extension(cog))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

        self.logger.info(
            Umbrella.LOADING_SUCCESS_MESSAGE("Extensions", self.extensions.keys())
        )

        self.logger.info(
            Umbrella.LOADING_SUCCESS_MESSAGE("App Commands", self.tree.get_commands())
        )
