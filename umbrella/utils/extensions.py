"""Utilities for loading Discord extensions."""

from importlib import import_module
from inspect import isfunction
from pkgutil import walk_packages
from types import ModuleType


def get_module_names(module: ModuleType) -> frozenset[str]:
    """
    Return all valid extension names from the given module.

    Args:
        module (types.ModuleType): The module containing extensions.

    Returns:
        An immutable set of strings of valid extension names for use by
        :obj:`discord.ext.commands.Bot.load_extension`
    """
    modules = set()

    for module_info in walk_packages(module.__path__, f"{module.__name__}."):
        imported_module = import_module(module_info.name)
        if not isfunction(getattr(imported_module, "setup", None)):
            # any files without a setup function will be ignored
            continue

        modules.add(module_info.name)

    return frozenset(modules)
