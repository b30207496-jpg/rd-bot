import datetime
import discord
from discord import app_commands
from discord.ext import commands


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="birthday_set", description="Set your birthday as MM/DD")
    async def birthday_set(self, interaction, date: str):
        try:
            month, day = map(int, date.split("/"))
            datetime.date(2024, month, day)
        except Exception:
            return await interaction.response.send_message("Use `MM/DD`, for example `08/27`.")
        await self.bot.db.execute(
            "INSERT INTO birthdays(guild_id,user_id,month,day) VALUES(?,?,?,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET month=excluded.month,day=excluded.day",
            (interaction.guild.id, interaction.user.id, month, day)
        )
        await interaction.response.send_message(f"🎂 Birthday saved as **{month:02d}/{day:02d}**.")

    @app_commands.command(name="birthday_view", description="View a member's birthday")
    async def birthday_view(self, interaction, member: discord.Member = None):
        member = member or interaction.user
        row = await self.bot.db.fetchone("SELECT month,day FROM birthdays WHERE guild_id=? AND user_id=?", (interaction.guild.id,member.id))
        await interaction.response.send_message(f"🎂 {member.mention}: **{row['month']:02d}/{row['day']:02d}**" if row else "No birthday saved.")

    @app_commands.command(name="birthday_remove", description="Remove your birthday")
    async def birthday_remove(self, interaction):
        await self.bot.db.execute("DELETE FROM birthdays WHERE guild_id=? AND user_id=?", (interaction.guild.id,interaction.user.id))
        await interaction.response.send_message("✅ Birthday removed.")


async def setup(bot):
    await bot.add_cog(Birthday(bot))
