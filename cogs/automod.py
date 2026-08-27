import datetime
import discord
from discord import app_commands
from discord.ext import commands
import time


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam = {}

        self.bad_words = {
            "badword1",
            "badword2",
            "badword3",
        }

    @app_commands.command(
        name="automod",
        description="Show AutoMod status"
    )
    async def automod(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🛡️ **AutoMod is active!**\n"
            "• 🚫 Bad-word filter\n"
            "• 🔗 Link filter\n"
            "• ⚡ Anti-spam"
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        content = message.content.lower()

        # Bad-word filter
        if any(word in content for word in self.bad_words):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, that message was removed.",
                    delete_after=5
                )
            except discord.Forbidden:
                pass
            return

        # Basic link filter
        if "http://" in content or "https://" in content:
            if not message.author.guild_permissions.manage_messages:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"🔗 {message.author.mention}, links aren't allowed here.",
                        delete_after=5
                    )
                except discord.Forbidden:
                    pass
                return

        # Anti-spam
        user_id = message.author.id
        now = time.time()

        timestamps = self.spam.get(user_id, [])
        timestamps = [t for t in timestamps if now - t < 5]
        timestamps.append(now)
        self.spam[user_id] = timestamps

        if len(timestamps) >= 6:
            try:
                await message.delete()
                await message.author.timeout(
                    discord.utils.utcnow() + datetime.timedelta(seconds=30),
                    reason="AutoMod anti-spam"
                )
            except (discord.Forbidden, discord.HTTPException):
                pass


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
