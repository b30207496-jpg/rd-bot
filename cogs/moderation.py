import time
import discord
import datetime
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned **{member}** — {reason}")

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked **{member}** — {reason}")

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction, member: discord.Member, minutes: app_commands.Range[int, 1, 40320], reason: str = "No reason provided"):
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minutes), reason=reason)
        await interaction.response.send_message(f"⏳ Timed out **{member}** for {minutes} minutes.")

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction, member: discord.Member, reason: str = "No reason provided"):
        await self.bot.db.execute(
            "INSERT INTO warnings(guild_id,user_id,moderator_id,reason,created_at) VALUES(?,?,?,?,?)",
            (interaction.guild.id, member.id, interaction.user.id, reason, int(time.time()))
        )
        await interaction.response.send_message(f"⚠️ Warned **{member}** — {reason}")

    @app_commands.command(name="warnings", description="View a member's warnings")
    async def warnings(self, interaction, member: discord.Member):
        rows = await self.bot.db.fetchall(
            "SELECT reason, moderator_id, created_at FROM warnings WHERE guild_id=? AND user_id=? ORDER BY id DESC LIMIT 10",
            (interaction.guild.id, member.id)
        )
        if not rows:
            return await interaction.response.send_message("✅ No warnings found.")
        text = "\n".join(
            f"• <t:{r['created_at']}:d> — {r['reason']} (mod <@{r['moderator_id']}>)"
            for r in rows
        )
        await interaction.response.send_message(f"⚠️ Warnings for {member.mention}\n{text}")

    @app_commands.command(name="clear", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
