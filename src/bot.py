import discord
from discord.ext import commands
import os
import sys
import asyncio
from dotenv import load_dotenv

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SRC_DIR)
sys.path.insert(0, SRC_DIR)

load_dotenv(os.path.join(os.path.dirname(SRC_DIR), ".env"))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

EXTENSIONS = [
    "commands.link",
    "commands.linklog",
    "commands.cd",
    "commands.flag",
    "commands.unflag",
    "commands.filter",
    "events.link_filter"
]

async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            print(f"Loaded: {extension}")
        except Exception as e:
            print(f"Failed to load {extension}: {e}")

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    print(f"Guilds: {len(bot.guilds)}")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync failed: {e}")

@bot.event
async def on_guild_join(guild):
    print(f"Joined: {guild.name}")
    try:
        await bot.tree.sync(guild=guild)
    except Exception as e:
        print(f"Sync failed for {guild.name}: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error in {event}: {sys.exc_info()}")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("DISCORD_TOKEN not found")
            print("Set DISCORD_TOKEN environment variable or create .env file")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
