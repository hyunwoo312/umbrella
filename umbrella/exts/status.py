import datetime

from discord.ext import tasks
from discord.ext.commands import Cog

from umbrella.umbrella import Umbrella


class Status(Cog):
    """
    An utility `Cog` for `Umbrella` status and custom server(s) status.
    """

    def __init__(self, umbrella: Umbrella, *args, **kwargs):
        super(*args, **kwargs)
        self.umbrella = umbrella

    @tasks.loop(seconds=60.0)
    async def fetch_online_users(self):
        pass

    @tasks.loop(time=datetime.time(), reconnect=True)
    async def create_server_backup(self):
        pass


async def setup(umbrella: Umbrella) -> None:
    """Load the Testing cog."""
    await umbrella.add_cog(Status(umbrella))
