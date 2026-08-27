import discord
from discord import app_commands
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        channel_id = await self.bot.db.setting(
            guild.id,
            "log_channel",
            ""
        )

        if not channel_id:
            return None

        return guild.get_channel(int(channel_id))

    async def send_log(self, guild, embed):
        channel = await self.get_log_channel(guild)

        if channel:
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                pass

    # =========================
    # LOG SETUP
    # =========================

    @app_commands.command(
        name="logsetup",
        description="Set the server logging channel"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logsetup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "log_channel",
            channel.id
        )

        await interaction.response.send_message(
            f"✅ Logging channel set to {channel.mention}.",
            ephemeral=True
        )

    # =========================
    # DISABLE LOGGING
    # =========================

    @app_commands.command(
        name="logdisable",
        description="Disable server logging"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logdisable(self, interaction: discord.Interaction):

        await self.bot.db.set_setting(
            interaction.guild.id,
            "log_channel",
            ""
        )

        await interaction.response.send_message(
            "✅ Server logging disabled.",
            ephemeral=True
        )

    # =========================
    # MEMBER JOIN
    # =========================

    @commands.Cog.listener()
    async def on_member_join(self, member):

        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="User",
            value=f"{member} (`{member.id}`)",
            inline=False
        )

        await self.send_log(member.guild, embed)

    # =========================
    # MEMBER LEAVE
    # =========================

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        embed = discord.Embed(
            title="📤 Member Left",
            description=f"**{member}** left the server.",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="User ID",
            value=f"`{member.id}`",
            inline=False
        )

        await self.send_log(member.guild, embed)

    # =========================
    # MESSAGE DELETE
    # =========================

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if not message.guild or message.author.bot:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Author",
            value=f"{message.author.mention}",
            inline=True
        )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=True
        )

        content = message.content or "*No text content*"

        embed.add_field(
            name="Content",
            value=content[:1000],
            inline=False
        )

        await self.send_log(message.guild, embed)

    # =========================
    # MESSAGE EDIT
    # =========================

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if not before.guild or before.author.bot:
            return

        if before.content == after.content:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.yellow()
        )

        embed.add_field(
            name="Author",
            value=before.author.mention,
            inline=True
        )

        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=True
        )

        embed.add_field(
            name="Before",
            value=(before.content or "*Empty*")[:1000],
            inline=False
        )

        embed.add_field(
            name="After",
            value=(after.content or "*Empty*")[:1000],
            inline=False
        )

        await self.send_log(before.guild, embed)

    # =========================
    # ROLE CREATE
    # =========================

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):

        embed = discord.Embed(
            title="🎭 Role Created",
            description=f"Role **{role.name}** was created.",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Role ID",
            value=f"`{role.id}`"
        )

        await self.send_log(role.guild, embed)

    # =========================
    # ROLE DELETE
    # =========================

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        embed = discord.Embed(
            title="🗑️ Role Deleted",
            description=f"Role **{role.name}** was deleted.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Role ID",
            value=f"`{role.id}`"
        )

        await self.send_log(role.guild, embed)

    # =========================
    # CHANNEL CREATE
    # =========================

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        embed = discord.Embed(
            title="📁 Channel Created",
            description=f"{channel.mention} was created.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Channel ID",
            value=f"`{channel.id}`"
        )

        await self.send_log(channel.guild, embed)

    # =========================
    # CHANNEL DELETE
    # =========================

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        embed = discord.Embed(
            title="🗑️ Channel Deleted",
            description=f"**{channel.name}** was deleted.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Channel ID",
            value=f"`{channel.id}`"
        )

        await self.send_log(channel.guild, embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))
