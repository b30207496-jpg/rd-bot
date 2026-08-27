import os
import logging
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from database import Database
from help_menu import HelpView

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("all-in-one-bot")


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/help"
            )
        )
        self.db = Database("bot.db")

    async def setup_hook(self):
        await self.db.connect()

        extensions = [
            "cogs.core",
            "cogs.community",
            "cogs.moderation",
            "cogs.utility",
            "cogs.fun",
            "cogs.economy",
            "cogs.leveling",
            "cogs.welcome",
            "cogs.logging_cog",
            "cogs.ticket",
            "cogs.verification",
            "cogs.reactionroles",
            "cogs.giveaway",
            "cogs.jointocreate",
            "cogs.tools",
            "cogs.search",
            "cogs.serverstats",
            "cogs.birthday",
            "cogs.music",
        ]
        for ext in extensions:
            try:
                await self.load_extension(ext)
            except Exception:
                log.exception("Could not load %s", ext)

        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d commands to guild %s", len(synced), GUILD_ID)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global commands", len(synced))

    async def close(self):
        await self.db.close()
        await super().close()


bot = Bot()


@bot.tree.command(name="help", description="Open the interactive command center")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Command Center",
        description=(
            "Select a category below to view its commands.\n\n"
            "This menu is designed like the command browser in your example."
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"{interaction.guild.name if interaction.guild else 'Discord'} • All-in-One Bot")
    await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    log.error("Command error", exc_info=error)
    message = "❌ Something went wrong while running that command."
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ You don't have permission to use this command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        message = "❌ I don't have the required permissions."
    elif isinstance(error, app_commands.CommandOnCooldown):
        message = f"⏳ Try again in {error.retry_after:.1f}s."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id)


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Put it in Railway Variables or .env.")

bot.run(TOKEN)
