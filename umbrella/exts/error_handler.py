from discord.ext.commands import Cog, Context, errors

from umbrella.umbrella import Umbrella


class ErrorHandler(Cog):
    """Handles errors emitted from commands."""

    def __init__(self, umbrella: Umbrella, *args, **kwargs):
        super(*args, **kwargs)
        self.umbrella = umbrella

    @Cog.listener()
    async def on_command_error(self, context: Context, e: errors.CommandError) -> None:
        if isinstance(e, errors.CheckFailure):
            await self.handle_check_failure(context, e)

    @staticmethod
    async def handle_check_failure(context: Context, e: errors.CheckFailure) -> None:
        if isinstance(e, errors.NoPrivateMessage):
            await context.send(e)


async def setup(umbrella: Umbrella) -> None:
    """Load the ErrorHandler cog."""
    await umbrella.add_cog(ErrorHandler(umbrella))
