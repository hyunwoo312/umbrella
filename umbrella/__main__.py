import asyncio

from discord import Intents

import umbrella
from umbrella.constants import BotConfig
from umbrella.umbrella import Umbrella


async def main() -> None:
    """Asynchronously initialises the bot"""
    intents = Intents.default()
    intents.presences = False
    intents.dm_typing = False
    intents.dm_reactions = False
    intents.invites = False
    intents.webhooks = False
    intents.integrations = False
    intents.message_content = True

    umbrella.instance = Umbrella(
        application_id=BotConfig.discord_app_id,
        case_insensitive=True,
        command_prefix=BotConfig.prefix,
        description="",
        intents=intents,
        strip_after_prefix=False,
    )
    async with umbrella.instance as server:
        await server.start(BotConfig.discord_token)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    exit(0)
