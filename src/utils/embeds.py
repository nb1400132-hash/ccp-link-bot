import discord
from datetime import datetime

class Colors:
    PRIMARY = 0x5865F2
    SUCCESS = 0x57F287
    WARNING = 0xFEE75C
    ERROR = 0xED4245
    DARK = 0x2f3136
    BLURPLE = 0x5865F2

def create_link_embed(author_name: str, has_password: bool, ask_username: bool) -> discord.Embed:
    embed = discord.Embed(
        title="Link Available",
        description="A new link has been shared. Click the button below to access it.",
        color=Colors.BLURPLE,
        timestamp=datetime.now()
    )
    
    info_parts = []
    if has_password:
        info_parts.append("Password Protected")
    if ask_username:
        info_parts.append("Username Required")
    
    if info_parts:
        embed.add_field(
            name="Requirements",
            value=" | ".join(info_parts),
            inline=False
        )
    
    embed.set_footer(text=f"Shared by {author_name}")
    return embed

def create_access_embed(link: str, password: str = None, username: str = None) -> discord.Embed:
    embed = discord.Embed(
        title="Access Granted",
        color=Colors.SUCCESS,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Link",
        value=f"```{link}```",
        inline=False
    )
    
    if password:
        embed.add_field(
            name="Password",
            value=f"```{password}```",
            inline=False
        )
    
    if username:
        embed.add_field(
            name="Your Username",
            value=f"```{username}```",
            inline=False
        )
    
    embed.set_footer(text="This message is only visible to you")
    return embed

def create_flagged_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Early Thug Attempt Detected",
        description="You early thugged and thats your fault! Please ask a admin to take you off this list.",
        color=Colors.ERROR,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Access Denied")
    return embed

def create_log_embed(link: str, password: str, ask_username: bool, author: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title="New Link Created",
        color=Colors.PRIMARY,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Link",
        value=f"||{link}||",
        inline=False
    )
    
    if password:
        embed.add_field(
            name="Password",
            value=f"||{password}||",
            inline=True
        )
    
    embed.add_field(
        name="Username Required",
        value="Yes" if ask_username else "No",
        inline=True
    )
    
    embed.add_field(
        name="Created By",
        value=f"{author.mention} ({author.name})",
        inline=False
    )
    
    embed.set_footer(text=f"ID: {author.id}")
    return embed

def create_access_log_embed(user: discord.Member, entered_username: str = None) -> discord.Embed:
    embed = discord.Embed(
        title="Link Accessed",
        color=Colors.SUCCESS,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="User",
        value=user.name,
        inline=True
    )
    
    embed.add_field(
        name="User ID",
        value=str(user.id),
        inline=True
    )
    
    embed.add_field(
        name="Mention",
        value=user.mention,
        inline=True
    )
    
    embed.add_field(
        name="Date Accessed",
        value=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        inline=False
    )
    
    if entered_username:
        embed.add_field(
            name="Entered Username",
            value=f"```{entered_username}```",
            inline=False
        )
    
    return embed

def create_flagged_attempt_embed(user: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title="Flagged User Attempt",
        description="A flagged user attempted to access a link",
        color=Colors.ERROR,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="User",
        value=user.name,
        inline=True
    )
    
    embed.add_field(
        name="User ID",
        value=str(user.id),
        inline=True
    )
    
    embed.add_field(
        name="Mention",
        value=user.mention,
        inline=True
    )
    
    embed.add_field(
        name="Date",
        value=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        inline=False
    )
    
    embed.add_field(
        name="Status",
        value="BLOCKED",
        inline=False
    )
    
    return embed

def create_success_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=Colors.SUCCESS,
        timestamp=datetime.now()
    )

def create_error_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=Colors.ERROR,
        timestamp=datetime.now()
    )

def create_info_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=Colors.PRIMARY,
        timestamp=datetime.now()
    )
