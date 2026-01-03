import discord
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
import json
import os
import re
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"linklog_channel": None, "flagged_users": [], "cooldown": 0, "active_links": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

class UsernameModal(Modal):
    def __init__(self, link_data, thread_id):
        super().__init__(title="Enter Your Username")
        self.link_data = link_data
        self.thread_id = thread_id
        self.username_input = TextInput(
            label="Username",
            placeholder="Type your username here",
            required=True,
            max_length=100
        )
        self.add_item(self.username_input)

    async def on_submit(self, interaction: discord.Interaction):
        entered_username = self.username_input.value
        
        embed = discord.Embed(
            title="Link Access Granted",
            color=0x2f3136
        )
        embed.add_field(name="Link", value=self.link_data["link"], inline=False)
        if self.link_data.get("password"):
            embed.add_field(name="Password", value=self.link_data["password"], inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await log_access(interaction, self.link_data, self.thread_id, entered_username)

class LinkButton(Button):
    def __init__(self, link_data, thread_id):
        super().__init__(label="Click to Access Link", style=discord.ButtonStyle.primary)
        self.link_data = link_data
        self.thread_id = thread_id

    async def callback(self, interaction: discord.Interaction):
        global data
        data = load_data()
        
        user_id = str(interaction.user.id)
        if user_id in data["flagged_users"]:
            embed = discord.Embed(
                title="Early Thug Attempt Detected",
                description="You early thugged and thats your fault! Please ask a admin to take you off this list.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await log_flagged_attempt(interaction, self.link_data, self.thread_id)
            return
        
        if self.link_data.get("ask_username"):
            modal = UsernameModal(self.link_data, self.thread_id)
            await interaction.response.send_modal(modal)
        else:
            embed = discord.Embed(
                title="Link Access Granted",
                color=0x2f3136
            )
            embed.add_field(name="Link", value=self.link_data["link"], inline=False)
            if self.link_data.get("password"):
                embed.add_field(name="Password", value=self.link_data["password"], inline=False)
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await log_access(interaction, self.link_data, self.thread_id, None)

class LinkView(View):
    def __init__(self, link_data, thread_id):
        super().__init__(timeout=None)
        self.add_item(LinkButton(link_data, thread_id))

async def log_access(interaction: discord.Interaction, link_data, thread_id, entered_username):
    global data
    data = load_data()
    
    if not data.get("linklog_channel"):
        return
    
    channel = interaction.client.get_channel(int(data["linklog_channel"]))
    if not channel:
        return
    
    if thread_id:
        thread = channel.get_thread(int(thread_id))
        if thread:
            embed = discord.Embed(
                title="Link Accessed",
                color=0x00ff00
            )
            embed.add_field(name="User", value=interaction.user.name, inline=True)
            embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
            embed.add_field(name="Mention", value=interaction.user.mention, inline=True)
            embed.add_field(name="Date Accessed", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            if entered_username:
                embed.add_field(name="Entered Username", value=entered_username, inline=False)
            
            await thread.send(embed=embed)

async def log_flagged_attempt(interaction: discord.Interaction, link_data, thread_id):
    global data
    data = load_data()
    
    if not data.get("linklog_channel"):
        return
    
    channel = interaction.client.get_channel(int(data["linklog_channel"]))
    if not channel:
        return
    
    if thread_id:
        thread = channel.get_thread(int(thread_id))
        if thread:
            embed = discord.Embed(
                title="Flagged User Attempt",
                color=0xff0000
            )
            embed.add_field(name="User", value=interaction.user.name, inline=True)
            embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
            embed.add_field(name="Mention", value=interaction.user.mention, inline=True)
            embed.add_field(name="Date", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Status", value="BLOCKED - User is flagged", inline=False)
            
            await thread.send(embed=embed)

@tree.command(name="link", description="Create a link with optional username prompt and password")
@app_commands.describe(
    linkhere="The link to share (required)",
    askusername="Whether to ask for username before showing link",
    password="Optional password to display with the link"
)
async def link_command(
    interaction: discord.Interaction,
    linkhere: str,
    askusername: bool = False,
    password: str = None
):
    global data
    data = load_data()
    
    link_data = {
        "link": linkhere,
        "ask_username": askusername,
        "password": password,
        "created_by": interaction.user.id,
        "created_at": datetime.now().isoformat()
    }
    
    thread_id = None
    
    if data.get("linklog_channel"):
        log_channel = interaction.client.get_channel(int(data["linklog_channel"]))
        if log_channel:
            log_embed = discord.Embed(
                title="New Link Created",
                color=0x2f3136
            )
            log_embed.add_field(name="Link", value=linkhere, inline=False)
            if password:
                log_embed.add_field(name="Password", value=password, inline=False)
            log_embed.add_field(name="Ask Username", value="Yes" if askusername else "No", inline=True)
            log_embed.add_field(name="Created By", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Date", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            
            log_message = await log_channel.send(embed=log_embed)
            
            thread = await log_message.create_thread(name=f"Access Log - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            thread_id = str(thread.id)
    
    embed = discord.Embed(
        title="Link Available",
        description="Click the button below to access this link.",
        color=0x2f3136
    )
    if password:
        embed.add_field(name="Password Protected", value="Yes", inline=True)
    if askusername:
        embed.add_field(name="Username Required", value="Yes", inline=True)
    embed.set_footer(text=f"Posted by {interaction.user.name}")
    
    view = LinkView(link_data, thread_id)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="linklog", description="Set the channel for logging link access")
@app_commands.describe(channelhere="The channel to send logs to")
async def linklog_command(interaction: discord.Interaction, channelhere: discord.TextChannel):
    global data
    data = load_data()
    
    data["linklog_channel"] = str(channelhere.id)
    save_data(data)
    
    embed = discord.Embed(
        title="Link Log Channel Set",
        description=f"Link access logs will now be sent to {channelhere.mention}",
        color=0x2f3136
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="cd", description="Set cooldown time for link access")
@app_commands.describe(time="Cooldown time (e.g., 30s, 2m). Max 4 minutes")
async def cd_command(interaction: discord.Interaction, time: str):
    global data
    data = load_data()
    
    match = re.match(r'^(\d+)(s|m)$', time.lower())
    if not match:
        embed = discord.Embed(
            title="Invalid Format",
            description="Please use format like 30s for seconds or 2m for minutes",
            color=0xff0000
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
        embed = discord.Embed(
            title="Cooldown Too Long",
            description="Maximum cooldown is 4 minutes (240s or 4m)",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data["cooldown"] = seconds
    save_data(data)
    
    embed = discord.Embed(
        title="Cooldown Set",
        description=f"Link access cooldown has been set to {time}",
        color=0x2f3136
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="flag", description="Flag a user to prevent them from accessing links")
@app_commands.describe(username="User ID, mention, or username of the person to flag")
async def flag_command(interaction: discord.Interaction, username: str):
    global data
    data = load_data()
    
    user_id = None
    
    mention_match = re.match(r'<@!?(\d+)>', username)
    if mention_match:
        user_id = mention_match.group(1)
    elif username.isdigit():
        user_id = username
    else:
        for member in interaction.guild.members:
            if member.name.lower() == username.lower() or (member.nick and member.nick.lower() == username.lower()):
                user_id = str(member.id)
                break
    
    if not user_id:
        embed = discord.Embed(
            title="User Not Found",
            description="Could not find a user with that ID, mention, or username",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user_id in data["flagged_users"]:
        embed = discord.Embed(
            title="Already Flagged",
            description="This user is already flagged",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data["flagged_users"].append(user_id)
    save_data(data)
    
    try:
        user = await interaction.client.fetch_user(int(user_id))
        user_display = f"{user.name} ({user_id})"
    except:
        user_display = user_id
    
    embed = discord.Embed(
        title="User Flagged",
        description=f"{user_display} has been flagged and can no longer access links",
        color=0x2f3136
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="unflag", description="Remove a user from the flagged list")
@app_commands.describe(username="User ID, mention, or username of the person to unflag")
async def unflag_command(interaction: discord.Interaction, username: str):
    global data
    data = load_data()
    
    user_id = None
    
    mention_match = re.match(r'<@!?(\d+)>', username)
    if mention_match:
        user_id = mention_match.group(1)
    elif username.isdigit():
        user_id = username
    else:
        for member in interaction.guild.members:
            if member.name.lower() == username.lower() or (member.nick and member.nick.lower() == username.lower()):
                user_id = str(member.id)
                break
    
    if not user_id:
        embed = discord.Embed(
            title="User Not Found",
            description="Could not find a user with that ID, mention, or username",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user_id not in data["flagged_users"]:
        embed = discord.Embed(
            title="Not Flagged",
            description="This user is not currently flagged",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data["flagged_users"].remove(user_id)
    save_data(data)
    
    try:
        user = await interaction.client.fetch_user(int(user_id))
        user_display = f"{user.name} ({user_id})"
    except:
        user_display = user_id
    
    embed = discord.Embed(
        title="User Unflagged",
        description=f"{user_display} has been unflagged and can now access links again",
        color=0x2f3136
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot is ready. Logged in as {client.user}")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Please set DISCORD_TOKEN environment variable")
else:
    client.run(TOKEN)
