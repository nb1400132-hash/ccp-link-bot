import discord
from discord import app_commands
from discord.ext import commands
import re
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.embeds import create_error_embed

class CooldownCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="cd", description="Start a countdown timer")
    @app_commands.describe(time="Countdown time (e.g., 30s for seconds, 2m for minutes). Max 4 minutes")
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
        else:
            seconds = value * 60
        
        if seconds > 240:
            embed = create_error_embed(
                title="Countdown Too Long",
                description="Maximum countdown is 4 minutes.\n\nValid examples:\n- `240s` (4 minutes)\n- `4m` (4 minutes)"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if seconds <= 0:
            embed = create_error_embed(
                title="Invalid Value",
                description="Countdown must be a positive number."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = self._create_countdown_embed(seconds)
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        remaining = seconds
        while remaining > 0:
            await asyncio.sleep(1)
            remaining -= 1
            
            if remaining > 0:
                embed = self._create_countdown_embed(remaining)
                await message.edit(embed=embed)
        
        final_embed = discord.Embed(
            title="🇮🇱 !! THUG !! 🇮🇱",
            color=0x5865F2
        )
        await message.edit(embed=final_embed)

    def _create_countdown_embed(self, seconds: int) -> discord.Embed:
        minutes = seconds // 60
        secs = seconds % 60
        
        if minutes > 0:
            time_display = f"{minutes}:{secs:02d}"
        else:
            time_display = f"{secs}"
        
        embed = discord.Embed(
            title="Countdown",
            description=f"# {time_display}",
            color=0x5865F2
        )
        return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(CooldownCommand(bot))
