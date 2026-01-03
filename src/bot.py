import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

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
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print(f"Connected to {len(bot.guilds)} guild(s)")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name} ({guild.id})")
    try:
        await bot.tree.sync(guild=guild)
    except Exception as e:
        print(f"Failed to sync commands for guild {guild.name}: {e}")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("Error: DISCORD_TOKEN not found in environment variables")
            print("Please create a .env file with DISCORD_TOKEN=your_token_here")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
