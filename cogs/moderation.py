import time
import datetime
import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def can_moderate(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot moderate yourself.",
                ephemeral=True
            )
            return False

        if member == interaction.guild.owner:
            await interaction.response.send_message(
                "❌ You cannot moderate the server owner.",
                ephemeral=True
            )
            return False

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ You cannot moderate a member with an equal or higher role.",
                ephemeral=True
            )
            return False

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ My role must be higher than that member's role.",
                ephemeral=True
            )
            return False

        return True

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not await self.can_moderate(interaction, member):
            return

        await member.ban(reason=reason)

        await interaction.response.send_message(
            f"🔨 Banned **{member}** — {reason}"
        )

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str
    ):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)

            await interaction.response.send_message(
                f"✅ Unbanned **{user}**."
            )

        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid user ID.",
                ephemeral=True
            )

        except discord.NotFound:
            await interaction.response.send_message(
                "❌ That user is not banned.",
                ephemeral=True
            )

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not await self.can_moderate(interaction, member):
            return

        await member.kick(reason=reason)

        await interaction.response.send_message(
            f"👢 Kicked **{member}** — {reason}"
        )

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str = "No reason provided"
    ):
        if not await self.can_moderate(interaction, member):
            return

        until = discord.utils.utcnow() + datetime.timedelta(
            minutes=minutes
        )

        await member.timeout(until, reason=reason)

        await interaction.response.send_message(
            f"⏳ Timed out **{member}** for **{minutes} minutes** — {reason}"
        )

    @app_commands.command(name="untimeout", description="Remove a member's timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        if not await self.can_moderate(interaction, member):
            return

        await member.timeout(None, reason="Timeout removed")

        await interaction.response.send_message(
            f"✅ Removed timeout from **{member}**."
        )

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not await self.can_moderate(interaction, member):
            return

        await self.bot.db.execute(
            """
            INSERT INTO warnings
            (guild_id, user_id, moderator_id, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                interaction.guild.id,
                member.id,
                interaction.user.id,
                reason,
                int(time.time())
            )
        )

        await interaction.response.send_message(
            f"⚠️ Warned **{member}** — {reason}"
        )

    @app_commands.command(
        name="warnings",
        description="View a member's warnings"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        rows = await self.bot.db.fetchall(
            """
            SELECT reason, moderator_id, created_at
            FROM warnings
            WHERE guild_id=? AND user_id=?
            ORDER BY id DESC
            LIMIT 10
            """,
            (interaction.guild.id, member.id)
        )

        if not rows:
            return await interaction.response.send_message(
                f"✅ **{member}** has no warnings."
            )

        text = "\n".join(
            f"• <t:{r['created_at']}:d> — {r['reason']} "
            f"(by <@{r['moderator_id']}>)"
            for r in rows
        )

        await interaction.response.send_message(
            f"⚠️ Warnings for **{member}**\n{text}"
        )

    @app_commands.command(name="clear", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🧹 Deleted **{len(deleted)}** messages.",
            ephemeral=True
        )

    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🧹 Purged **{len(deleted)}** messages.",
            ephemeral=True
        )

    @app_commands.command(name="lock", description="Lock this channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        channel = interaction.channel

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False

        await channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "🔒 Channel locked."
        )

    @app_commands.command(name="unlock", description="Unlock this channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        channel = interaction.channel

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None

        await channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "🔓 Channel unlocked."
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
