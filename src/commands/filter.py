import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data import get_filter_enabled, set_filter_enabled
from utils.embeds import create_success_embed

class FilterToggleCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="filter", description="Enable or disable the link filter")
    @app_commands.describe(enabled="Enable or disable the link filter")
    @app_commands.default_permissions(administrator=True)
    async def filter_toggle(
        self,
        interaction: discord.Interaction,
        enabled: bool
    ):
        set_filter_enabled(interaction.guild_id, enabled)
        
        if enabled:
            embed = create_success_embed(
                title="Link Filter Enabled",
                description="The link filter is now active.\n\nZoom, Discord invites, Webex, and Google Meet links will be automatically deleted."
            )
        else:
            embed = create_success_embed(
                title="Link Filter Disabled",
                description="The link filter has been disabled.\n\nUsers can now post any links freely."
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(FilterToggleCommand(bot))
