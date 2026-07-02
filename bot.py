import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from db import close_db, init_db

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dtm-bot")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def load_cogs() -> None:
    cogs_dir = Path(__file__).parent / "cogs"
    for path in cogs_dir.glob("*.py"):
        if path.stem.startswith("_"):
            continue
        extension = f"cogs.{path.stem}"
        try:
            await bot.load_extension(extension)
            logger.info("Loaded cog: %s", extension)
        except Exception:
            logger.exception("Failed to load cog: %s", extension)


@bot.event
async def on_ready() -> None:
    logger.info("Logged in as %s (id=%s)", bot.user, bot.user.id if bot.user else "?")

    if GUILD_ID:
        guild = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        logger.info("Synced %d command(s) to guild %s", len(synced), GUILD_ID)
    else:
        synced = await bot.tree.sync()
        logger.info("Synced %d command(s) globally", len(synced))


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")

    await init_db()
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
