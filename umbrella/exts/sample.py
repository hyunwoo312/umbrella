from collections.abc import Callable

import discord
from discord import Interaction, app_commands
from discord.ext.commands import Cog, Context, command
from discord import SelectOption

from umbrella.umbrella import Umbrella
from umbrella.constants import PING_USER_ID

DEFAULT_MODAL_TIMEOUT = 180


class Sample(Cog):
    """ss."""

    def __init__(self, umbrella: Umbrella, *args, **kwargs):
        super(*args, **kwargs)
        self.umbrella = umbrella

    @app_commands.command()  # /test
    async def test(self, interaction: Interaction) -> None:
        # await interaction.response.send_message(view=DeleteConfirmationView(interaction.user))
        # await interaction.response.send_message(view=BooleanSelectView("suh"))
        await interaction.response.send_modal(FreeInputModal("yep", int))

    @command()  # !test
    async def test2(self, context: Context) -> None:
        # server_id = context.message.guild.id
        user_id = context.message.author.id
        # await context.send(context.message.author.mention + "sup")
        await context.send(PING_USER_ID(user_id))


class FreeInputModal(discord.ui.Modal):
    """A modal to freely enter a value for a setting."""

    def __init__(
        self, setting_name: str, type_: type, update_callback: Callable = None
    ):
        title = (
            f"{setting_name} Input" if len(setting_name) < 12 - 6 else "Setting Input"
        )
        super().__init__(timeout=DEFAULT_MODAL_TIMEOUT, title=title)

        self.setting_name = setting_name
        self.type_ = type_
        self.update_callback = update_callback

        label = setting_name if len(setting_name) < 12 else "Value"
        self.setting_input = discord.ui.TextInput(
            label=label, style=discord.TextStyle.paragraph, required=False
        )
        self.add_item(self.setting_input)

        self.select_view = BooleanSelectView("yee")
        self.add_item(self.select_view)

    async def on_submit(self, interaction: Interaction) -> None:
        """Update the setting with the new value in the embed."""
        try:
            if not self.setting_input.value:
                value = self.type_()
            else:
                value = self.type_(self.setting_input.value)
        except (ValueError, TypeError):
            await interaction.response.send_message(
                f"Could not process the input value for `{self.setting_name}`.",
                ephemeral=True,
            )
        else:
            # await self.update_callback(setting_name=self.setting_name, setting_value=value)
            await interaction.response.send_message(
                content="{} {}".format(value, self.setting_name), ephemeral=True
            )


class BooleanSelectView(discord.ui.View):
    """A view containing an instance of BooleanSelect."""

    class BooleanSelect(discord.ui.Select):
        """Select a true or false value and send it to the supplied callback."""

        def __init__(self, setting_name: str, update_callback: Callable):
            super().__init__(
                options=[SelectOption(label="True"), SelectOption(label="False")]
            )
            self.setting_name = setting_name
            self.update_callback = update_callback

        async def callback(self, interaction: Interaction) -> None:
            """Respond to the interaction by sending the boolean value to the update callback."""
            # value = self.values[0] == "True"
            # await self.update_callback(setting_name=self.setting_name, setting_value=value)
            await interaction.response.edit_message(
                content="✅ Edit for `{0}` confirmed".format(self.setting_name),
                view=None,
            )

    def __init__(self, setting_name: str, update_callback: Callable = None):
        super().__init__(timeout=180)
        self.add_item(self.BooleanSelect(setting_name, update_callback))


class DeleteConfirmationView(discord.ui.View):
    """A view to confirm a deletion."""

    def __init__(self, author, callback: Callable = None):
        super().__init__(timeout=180)
        self.author = author
        self.callback = callback

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Only allow interactions from the command invoker."""
        return interaction.user.id == self.author.id

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, row=0)
    async def confirm(
        self, interaction: Interaction, button: discord.ui.Button
    ) -> None:
        """Invoke the filter list deletion."""
        await interaction.response.edit_message(view=None)
        # await self.callback()

    @discord.ui.button(label="Cancel", row=0)
    async def cancel(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel the filter list deletion."""
        await interaction.response.edit_message(
            content="🚫 Operation canceled.", view=None
        )


async def setup(umbrella: Umbrella) -> None:
    """Load the Testing cog."""
    await umbrella.add_cog(Sample(umbrella))
    await umbrella.tree.sync()
