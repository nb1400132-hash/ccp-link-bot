import discord
from discord.ext import commands
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.embeds import create_error_embed
from utils.data import get_filter_enabled

BLOCKED_PATTERNS = [
    r'(?:https?://)?(?:www\.)?zoom\.us/[^\s]*',
    r'(?:https?://)?(?:www\.)?zoom\.com/[^\s]*',
    r'(?:https?://)?(?:www\.)?zoomgov\.com/[^\s]*',
    r'(?:https?://)?(?:[a-z0-9-]+\.)?zoom\.us/[^\s]*',
    r'(?:https?://)?(?:[a-z0-9-]+\.)?zoom\.com/[^\s]*',
    r'(?:https?://)?(?:[a-z0-9-]+\.)?zoomgov\.com/[^\s]*',
    
    r'(?:https?://)?discord\.gg/[^\s]+',
    r'(?:https?://)?(?:www\.)?discord\.com/invite/[^\s]+',
    r'(?:https?://)?(?:www\.)?discordapp\.com/invite/[^\s]+',
    r'(?:https?://)?(?:www\.)?discord\.com/channels/[^\s]*',
    r'(?:https?://)?(?:canary\.)?discord\.com/invite/[^\s]+',
    r'(?:https?://)?(?:ptb\.)?discord\.com/invite/[^\s]+',
    
    r'(?:https?://)?(?:www\.)?webex\.com/[^\s]*',
    r'(?:https?://)?(?:[a-z0-9-]+\.)?webex\.com/[^\s]*',
    
    r'(?:https?://)?meet\.google\.com/[^\s]*',
]

ALLOWED_PATTERNS = [
    r'(?:https?://)?cdn\.discordapp\.com/[^\s]*',
    r'(?:https?://)?media\.discordapp\.com/[^\s]*',
    r'(?:https?://)?images-ext-\d+\.discordapp\.net/[^\s]*',
    r'(?:https?://)?(?:www\.)?tenor\.com/[^\s]*',
    r'(?:https?://)?(?:www\.)?giphy\.com/[^\s]*',
    r'(?:https?://)?i\.imgur\.com/[^\s]*',
    r'(?:https?://)?cdn\.discord\.com/[^\s]*',
]

class LinkFilter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blocked_regex = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]
        self.allowed_regex = [re.compile(p, re.IGNORECASE) for p in ALLOWED_PATTERNS]

    def is_allowed_link(self, url: str) -> bool:
        for pattern in self.allowed_regex:
            if pattern.search(url):
                return True
        return False

    def contains_blocked_link(self, content: str) -> bool:
        for pattern in self.blocked_regex:
            matches = pattern.findall(content)
            for match in matches:
                if not self.is_allowed_link(match):
                    return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        if not get_filter_enabled(message.guild.id):
            return
        
        if self.contains_blocked_link(message.content):
            try:
                await message.delete()
                
                embed = create_error_embed(
                    title="Link Blocked",
                    description="Please use the `/link` command to post links.\n\nThis helps keep everyone safe and allows proper logging."
                )
                
                warning = await message.channel.send(
                    content=message.author.mention,
                    embed=embed
                )
                
                await warning.delete(delay=10)
                
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(LinkFilter(bot))
