import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data import set_linklog_channel
from utils.embeds import create_success_embed

class LinkLogCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="linklog", description="Set the channel for logging link access")
    @app_commands.describe(channelhere="The channel to send access logs to")
    @app_commands.default_permissions(administrator=True)
    async def linklog(
        self,
        interaction: discord.Interaction,
        channelhere: discord.TextChannel
    ):
        set_linklog_channel(interaction.guild_id, channelhere.id)
        
        embed = create_success_embed(
            title="Log Channel Set",
            description=f"Link access logs will now be sent to {channelhere.mention}\n\nEach new link will create a thread for tracking who accessed it."
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(LinkLogCommand(bot))
