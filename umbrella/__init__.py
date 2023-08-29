from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from umbrella.umbrella import Umbrella

instance: "Umbrella" = None  # Global Bot instance.
