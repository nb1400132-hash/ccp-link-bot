import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import uuid

from utils.data import get_linklog_channel
from utils.embeds import create_link_embed, create_log_embed, create_success_embed
from views.link_view import LinkView

class LinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="link", description="Share a link with optional password and username requirement")
    @app_commands.describe(
        linkhere="The link to share",
        askusername="Require users to enter their username before accessing",
        password="Optional password for the link"
    )
    async def link(
        self,
        interaction: discord.Interaction,
        linkhere: str,
        askusername: bool = False,
        password: str = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        link_id = str(uuid.uuid4())[:8]
        
        link_data = {
            "id": link_id,
            "link": linkhere,
            "ask_username": askusername,
            "password": password,
            "created_by": interaction.user.id,
            "created_at": datetime.now().isoformat()
        }
        
        thread_id = None
        
        try:
            linklog_channel_id = get_linklog_channel(interaction.guild_id)
            if linklog_channel_id:
                log_channel = interaction.client.get_channel(linklog_channel_id)
                if log_channel:
                    log_embed = create_log_embed(
                        link=linkhere,
                        password=password,
                        ask_username=askusername,
                        author=interaction.user
                    )
                    
                    log_message = await log_channel.send(embed=log_embed)
                    
                    thread = await log_message.create_thread(
                        name=f"Access Log - {datetime.now().strftime('%m/%d %H:%M')}"
                    )
                    thread_id = str(thread.id)
        except Exception as e:
            print(f"Linklog error: {e}")
        
        public_embed = create_link_embed(
            author_name=interaction.user.name,
            has_password=password is not None,
            ask_username=askusername
        )
        
        view = LinkView(link_data, thread_id)
        
        await interaction.channel.send(embed=public_embed, view=view)
        
        confirm_embed = create_success_embed(
            title="Link Created",
            description="Your link has been shared successfully."
        )
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(LinkCommand(bot))
