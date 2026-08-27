import random
import time
import discord
from discord import app_commands
from discord.ext import commands


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure(self, guild_id, user_id):
        await self.bot.db.execute(
            "INSERT OR IGNORE INTO economy(guild_id,user_id,balance,last_daily) VALUES(?,?,0,0)",
            (guild_id, user_id)
        )

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction, member: discord.Member = None):
        member = member or interaction.user
        await self.ensure(interaction.guild.id, member.id)
        row = await self.bot.db.fetchone(
            "SELECT balance FROM economy WHERE guild_id=? AND user_id=?",
            (interaction.guild.id, member.id)
        )
        await interaction.response.send_message(f"💰 **{member.display_name}** has **{row['balance']:,}** coins.")

    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction):
        gid, uid = interaction.guild.id, interaction.user.id
        await self.ensure(gid, uid)
        row = await self.bot.db.fetchone("SELECT balance,last_daily FROM economy WHERE guild_id=? AND user_id=?", (gid, uid))
        now = int(time.time())
        if now - row["last_daily"] < 86400:
            left = 86400 - (now - row["last_daily"])
            return await interaction.response.send_message(f"⏳ Come back in **{left//3600}h {(left%3600)//60}m**.")
        reward = random.randint(500, 1500)
        await self.bot.db.execute("UPDATE economy SET balance=balance+?,last_daily=? WHERE guild_id=? AND user_id=?", (reward, now, gid, uid))
        await interaction.response.send_message(f"🎁 You received **{reward:,}** coins!")

    @app_commands.command(name="work", description="Work for coins")
    async def work(self, interaction):
        reward = random.randint(100, 500)
        await self.ensure(interaction.guild.id, interaction.user.id)
        await self.bot.db.execute("UPDATE economy SET balance=balance+? WHERE guild_id=? AND user_id=?", (reward, interaction.guild.id, interaction.user.id))
        await interaction.response.send_message(f"💼 You earned **{reward:,}** coins.")

    @app_commands.command(name="pay", description="Pay another member")
    async def pay(self, interaction, member: discord.Member, amount: app_commands.Range[int, 1, 1000000]):
        gid, uid = interaction.guild.id, interaction.user.id
        if member.id == uid:
            return await interaction.response.send_message("❌ You can't pay yourself.")
        await self.ensure(gid, uid); await self.ensure(gid, member.id)
        row = await self.bot.db.fetchone("SELECT balance FROM economy WHERE guild_id=? AND user_id=?", (gid, uid))
        if row["balance"] < amount:
            return await interaction.response.send_message("❌ You don't have enough coins.")
        await self.bot.db.execute("UPDATE economy SET balance=balance-? WHERE guild_id=? AND user_id=?", (amount, gid, uid))
        await self.bot.db.execute("UPDATE economy SET balance=balance+? WHERE guild_id=? AND user_id=?", (amount, gid, member.id))
        await interaction.response.send_message(f"💸 Sent **{amount:,}** coins to {member.mention}.")

    @app_commands.command(name="leaderboard", description="Show the economy leaderboard")
    async def leaderboard(self, interaction):
        rows = await self.bot.db.fetchall("SELECT user_id,balance FROM economy WHERE guild_id=? ORDER BY balance DESC LIMIT 10", (interaction.guild.id,))
        text = "\n".join(f"**{i}.** <@{r['user_id']}> — `{r['balance']:,}`" for i, r in enumerate(rows, 1)) or "No data yet."
        await interaction.response.send_message(f"🏆 **Economy Leaderboard**\n{text}")


async def setup(bot):
    await bot.add_cog(Economy(bot))
