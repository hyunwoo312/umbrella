from typing import TYPE_CHECKING

from umbrella import log

if TYPE_CHECKING:
    from umbrella.umbrella import Umbrella

log.setup()

instance: "Umbrella" = None  # Global Bot instance.
