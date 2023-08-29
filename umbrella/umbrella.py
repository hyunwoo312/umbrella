from discord.ext import commands


class Umbrella(commands.Bot):
    """A subclass of `discord.ext.commands.Bot` that implements other functions."""

    def __init__(self, *args, **kwargs):
        """Initialize the bot instance `umbrella`."""
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        await super().setup_hook()
        return
