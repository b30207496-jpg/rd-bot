import random
import time
import discord
from discord import app_commands
from discord.ext import commands


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    async def add_xp(self, guild_id, user_id):
        now = time.time()
        key = (guild_id, user_id)

        # 60-second XP cooldown
        if key in self.cooldowns and now - self.cooldowns[key] < 60:
            return None

        self.cooldowns[key] = now

        row = await self.bot.db.fetchone(
            "SELECT xp, level FROM levels WHERE guild_id=? AND user_id=?",
            (guild_id, user_id)
        )

        if not row:
            xp = random.randint(10, 25)
            level = 0

            await self.bot.db.execute(
                "INSERT INTO levels(guild_id,user_id,xp,level) VALUES(?,?,?,?)",
                (guild_id, user_id, xp, level)
            )
        else:
            xp = row["xp"]
            level = row["level"]

            xp += random.randint(10, 25)

            needed = 100 + (level * 50)

            if xp >= needed:
                xp -= needed
                level += 1

                await self.bot.db.execute(
                    "UPDATE levels SET xp=?, level=? WHERE guild_id=? AND user_id=?",
                    (xp, level, guild_id, user_id)
                )

                return level

            await self.bot.db.execute(
                "UPDATE levels SET xp=? WHERE guild_id=? AND user_id=?",
                (xp, guild_id, user_id)
            )

        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        new_level = await self.add_xp(
            message.guild.id,
            message.author.id
        )

        if new_level:
            try:
                await message.channel.send(
                    f"🎉 {message.author.mention} reached **Level {new_level}**!"
                )
            except discord.HTTPException:
                pass

    @app_commands.command(
        name="rank",
        description="Show your level and XP"
    )
    async def rank(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
    ):
        member = member or interaction.user

        row = await self.bot.db.fetchone(
            "SELECT xp, level FROM levels WHERE guild_id=? AND user_id=?",
            (interaction.guild.id, member.id)
        )

        if not row:
            xp = 0
            level = 0
        else:
            xp = row["xp"]
            level = row["level"]

        needed = 100 + (level * 50)

        await interaction.response.send_message(
            f"📊 **{member.display_name}'s Rank**\n"
            f"🏆 Level: **{level}**\n"
            f"✨ XP: **{xp}/{needed}**"
        )

    @app_commands.command(
        name="levels",
        description="Show the level leaderboard"
    )
    async def levels(self, interaction: discord.Interaction):
        rows = await self.bot.db.fetchall(
            "SELECT user_id, level, xp FROM levels "
            "WHERE guild_id=? ORDER BY level DESC, xp DESC LIMIT 10",
            (interaction.guild.id,)
        )

        if not rows:
            return await interaction.response.send_message(
                "📊 No level data yet."
            )

        text = []

        for i, row in enumerate(rows, 1):
            text.append(
                f"**{i}.** <@{row['user_id']}> — "
                f"Level **{row['level']}** "
                f"({row['xp']} XP)"
            )

        await interaction.response.send_message(
            "🏆 **Level Leaderboard**\n\n" + "\n".join(text)
        )

    @app_commands.command(
        name="setlevel",
        description="Set a member's level"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlevel(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        level: app_commands.Range[int, 0, 1000]
    ):
        await self.bot.db.execute(
            "INSERT INTO levels(guild_id,user_id,xp,level) "
            "VALUES(?,?,0,?) "
            "ON CONFLICT(guild_id,user_id) "
            "DO UPDATE SET level=excluded.level,xp=0",
            (interaction.guild.id, member.id, level)
        )

        await interaction.response.send_message(
            f"✅ Set {member.mention} to level **{level}**."
        )


async def setup(bot):
    await bot.add_cog(Leveling(bot))
