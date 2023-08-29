import asyncio

from discord import Intents

import umbrella
from umbrella.constants import BotConfig
from umbrella.umbrella import Umbrella


async def main() -> None:
    """Asynchronously initialises the bot"""
    intents = Intents.default()
    intents.message_content = True
    intents.presences = False
    intents.dm_typing = False
    intents.dm_reactions = False
    intents.invites = False
    intents.webhooks = False
    intents.integrations = False

    umbrella.instance = Umbrella(
        command_prefix=BotConfig.prefix, case_insensitive=True, intents=intents
    )
    async with umbrella.instance as server:
        await server.start(BotConfig.token)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    exit(0)
