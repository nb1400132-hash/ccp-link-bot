import discord
from discord import app_commands
from discord.ext import commands
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data import set_cooldown
from utils.embeds import create_success_embed, create_error_embed

class CooldownCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="cd", description="Set cooldown time for link access")
    @app_commands.describe(time="Cooldown time (e.g., 30s for seconds, 2m for minutes). Max 4 minutes")
    @app_commands.default_permissions(administrator=True)
    async def cd(
        self,
        interaction: discord.Interaction,
        time: str
    ):
        match = re.match(r'^(\d+)(s|m)$', time.lower().strip())
        
        if not match:
            embed = create_error_embed(
                title="Invalid Format",
                description="Please use the correct format:\n- `30s` for 30 seconds\n- `2m` for 2 minutes"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == "s":
            seconds = value
            display_time = f"{value} second{'s' if value != 1 else ''}"
        else:
            seconds = value * 60
            display_time = f"{value} minute{'s' if value != 1 else ''}"
        
        if seconds > 240:
            embed = create_error_embed(
                title="Cooldown Too Long",
                description="Maximum cooldown is 4 minutes.\n\nValid examples:\n- `240s` (4 minutes)\n- `4m` (4 minutes)"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if seconds < 0:
            embed = create_error_embed(
                title="Invalid Value",
                description="Cooldown must be a positive number."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        set_cooldown(interaction.guild_id, seconds)
        
        if seconds == 0:
            embed = create_success_embed(
                title="Cooldown Disabled",
                description="Link access cooldown has been disabled."
            )
        else:
            embed = create_success_embed(
                title="Cooldown Set",
                description=f"Link access cooldown has been set to **{display_time}**."
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CooldownCommand(bot))
