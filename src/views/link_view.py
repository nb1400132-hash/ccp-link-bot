import discord
from discord.ui import Button, View, Modal, TextInput
from typing import Optional

from utils.data import is_user_flagged, get_linklog_channel
from utils.embeds import (
    create_access_embed,
    create_flagged_embed,
    create_access_log_embed,
    create_flagged_attempt_embed
)

class UsernameModal(Modal):
    def __init__(self, link_data: dict, thread_id: Optional[str]):
        super().__init__(title="Enter Your Username")
        self.link_data = link_data
        self.thread_id = thread_id
        
        self.username_input = TextInput(
            label="Username",
            placeholder="Enter the username you will be using",
            required=True,
            max_length=100,
            style=discord.TextStyle.short
        )
        self.add_item(self.username_input)

    async def on_submit(self, interaction: discord.Interaction):
        entered_username = self.username_input.value
        
        embed = create_access_embed(
            link=self.link_data["link"],
            password=self.link_data.get("password"),
            username=entered_username
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await self._log_access(interaction, entered_username)

    async def _log_access(self, interaction: discord.Interaction, entered_username: str):
        if not self.thread_id:
            return
        
        try:
            channel_id = get_linklog_channel(interaction.guild_id)
            if not channel_id:
                return
            
            channel = interaction.client.get_channel(channel_id)
            if not channel:
                return
            
            thread = channel.get_thread(int(self.thread_id))
            if thread:
                embed = create_access_log_embed(interaction.user, entered_username)
                await thread.send(embed=embed)
        except Exception as e:
            print(f"Log error: {e}")

class LinkButton(Button):
    def __init__(self, link_data: dict, thread_id: Optional[str]):
        super().__init__(
            label="Access Link",
            style=discord.ButtonStyle.primary,
            custom_id=f"link_access_{link_data.get('id', 'default')}"
        )
        self.link_data = link_data
        self.thread_id = thread_id

    async def callback(self, interaction: discord.Interaction):
        try:
            if is_user_flagged(interaction.guild_id, interaction.user.id):
                embed = create_flagged_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await self._log_flagged_attempt(interaction)
                return
            
            if self.link_data.get("ask_username"):
                modal = UsernameModal(self.link_data, self.thread_id)
                await interaction.response.send_modal(modal)
            else:
                embed = create_access_embed(
                    link=self.link_data["link"],
                    password=self.link_data.get("password")
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await self._log_access(interaction)
        except Exception as e:
            print(f"Button error: {e}")

    async def _log_access(self, interaction: discord.Interaction):
        if not self.thread_id:
            return
        
        try:
            channel_id = get_linklog_channel(interaction.guild_id)
            if not channel_id:
                return
            
            channel = interaction.client.get_channel(channel_id)
            if not channel:
                return
            
            thread = channel.get_thread(int(self.thread_id))
            if thread:
                embed = create_access_log_embed(interaction.user)
                await thread.send(embed=embed)
        except Exception as e:
            print(f"Log error: {e}")

    async def _log_flagged_attempt(self, interaction: discord.Interaction):
        if not self.thread_id:
            return
        
        try:
            channel_id = get_linklog_channel(interaction.guild_id)
            if not channel_id:
                return
            
            channel = interaction.client.get_channel(channel_id)
            if not channel:
                return
            
            thread = channel.get_thread(int(self.thread_id))
            if thread:
                embed = create_flagged_attempt_embed(interaction.user)
                await thread.send(embed=embed)
        except Exception as e:
            print(f"Log error: {e}")

class LinkView(View):
    def __init__(self, link_data: dict, thread_id: Optional[str]):
        super().__init__(timeout=None)
        self.add_item(LinkButton(link_data, thread_id))
