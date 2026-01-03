import discord
from discord import app_commands
from discord.ext import commands
import re

from utils.data import flag_user
from utils.embeds import create_success_embed, create_error_embed

class FlagCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="flag", description="Flag a user to prevent them from accessing links")
    @app_commands.describe(username="User ID, mention, or username of the person to flag")
    @app_commands.default_permissions(administrator=True)
    async def flag(
        self,
        interaction: discord.Interaction,
        username: str
    ):
        user_id = await self._resolve_user(interaction, username)
        
        if not user_id:
            embed = create_error_embed(
                title="User Not Found",
                description="Could not find a user with that ID, mention, or username.\n\nTry using:\n- User mention (@user)\n- User ID (123456789)\n- Exact username"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        success = flag_user(interaction.guild_id, user_id)
        
        if not success:
            embed = create_error_embed(
                title="Already Flagged",
                description="This user is already on the flagged list."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            user = await interaction.client.fetch_user(user_id)
            user_display = f"**{user.name}** (`{user_id}`)"
        except Exception:
            user_display = f"`{user_id}`"
        
        embed = create_success_embed(
            title="User Flagged",
            description=f"{user_display} has been flagged.\n\nThey will no longer be able to access links and their attempts will be logged."
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _resolve_user(self, interaction: discord.Interaction, username: str) -> int:
        mention_match = re.match(r'<@!?(\d+)>', username)
        if mention_match:
            return int(mention_match.group(1))
        
        if username.isdigit():
            return int(username)
        
        for member in interaction.guild.members:
            if member.name.lower() == username.lower():
                return member.id
            if member.nick and member.nick.lower() == username.lower():
                return member.id
            if member.display_name.lower() == username.lower():
                return member.id
        
        return None

async def setup(bot: commands.Bot):
    await bot.add_cog(FlagCommand(bot))
