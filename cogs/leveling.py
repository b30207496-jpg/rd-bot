import random
import discord
from discord import app_commands
from discord.ext import commands


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_xp(self, guild_id, user_id):
        row = await self.bot.db.fetchone("SELECT xp,level FROM levels WHERE guild_id=? AND user_id=?", (guild_id,user_id))
        if not row:
            await self.bot.db.execute("INSERT INTO levels(guild_id,user_id,xp,level) VALUES(?,?,?,0)", (guild_id,user_id,0))
            xp, level = 0, 0
        else:
            xp, level = row["xp"], row["level"]
        xp += random.randint(5, 15)
        needed = 100 + level * 50
        if xp >= needed:
            xp -= needed
            level += 1
        await self.bot.db.execute("UPDATE levels SET xp=?,level=? WHERE guild_id=? AND user_id=?", (xp,level,guild_id,user_id))

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.guild:
            await self.add_xp(message.guild.id, message.author.id)

    @app_commands.command(name="rank", description="Show your level")
    async def rank(self, interaction, member: discord.Member = None):
        member = member or interaction.user
        row = await self.bot.db.fetchone("SELECT xp,level FROM levels WHERE guild_id=? AND user_id=?", (interaction.guild.id, member.id))
        xp, level = (row["xp"], row["level"]) if row else (0,0)
        await interaction.response.send_message(f"📊 **{member.display_name}** — Level **{level}**, XP **{xp}**")

    @app_commands.command(name="levels", description="Show the level leaderboard")
    async def levels(self, interaction):
        rows = await self.bot.db.fetchall("SELECT user_id,level,xp FROM levels WHERE guild_id=? ORDER BY level DESC,xp DESC LIMIT 10", (interaction.guild.id,))
        text = "\n".join(f"**{i}.** <@{r['user_id']}> — Lvl {r['level']} ({r['xp']} XP)" for i,r in enumerate(rows,1)) or "No level data yet."
        await interaction.response.send_message(f"📊 **Level Leaderboard**\n{text}")

    @app_commands.command(name="setlevel", description="Set a member's level")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlevel(self, interaction, member: discord.Member, level: app_commands.Range[int,0,1000]):
        await self.bot.db.execute(
            "INSERT INTO levels(guild_id,user_id,xp,level) VALUES(?,?,0,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET level=excluded.level,xp=0",
            (interaction.guild.id,member.id,level)
        )
        await interaction.response.send_message(f"✅ Set {member.mention} to level **{level}**.")


async def setup(bot):
    await bot.add_cog(Leveling(bot))
