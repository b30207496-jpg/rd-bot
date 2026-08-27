import discord
from discord import app_commands
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="welcome_set",
        description="Set the welcome channel"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_set(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str = "Welcome {user} to {server}!"
    ):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "welcome_channel",
            str(channel.id)
        )

        await self.bot.db.set_setting(
            interaction.guild.id,
            "welcome_message",
            message
        )

        await interaction.response.send_message(
            f"👋 Welcome channel set to {channel.mention}."
        )

    @app_commands.command(
        name="welcome_disable",
        description="Disable welcome messages"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_disable(self, interaction: discord.Interaction):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "welcome_channel",
            ""
        )

        await interaction.response.send_message(
            "✅ Welcome messages disabled."
        )

    @app_commands.command(
        name="welcome_test",
        description="Test the welcome message"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_test(self, interaction: discord.Interaction):
        cid = await self.bot.db.setting(
            interaction.guild.id,
            "welcome_channel"
        )

        if not cid:
            return await interaction.response.send_message(
                "❌ Set a welcome channel first with `/welcome_set`.",
                ephemeral=True
            )

        channel = interaction.guild.get_channel(int(cid))

        if not channel:
            return await interaction.response.send_message(
                "❌ The configured welcome channel no longer exists.",
                ephemeral=True
            )

        await self.send_welcome(channel, interaction.user)

        await interaction.response.send_message(
            "✅ Welcome test sent!",
            ephemeral=True
        )

    async def send_welcome(self, channel, member):
        message = await self.bot.db.setting(
            member.guild.id,
            "welcome_message",
            "Welcome {user} to {server}!"
        )

        message = message.replace(
            "{user}",
            member.mention
        ).replace(
            "{server}",
            member.guild.name
        )

        embed = discord.Embed(
            title="👋 Welcome!",
            description=message,
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="👥 Members",
            value=f"**{member.guild.member_count}**",
            inline=True
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Welcome to {member.guild.name}!"
        )

        await channel.send(
            content=member.mention,
            embed=embed
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cid = await self.bot.db.setting(
            member.guild.id,
            "welcome_channel"
        )

        if not cid:
            return

        channel = member.guild.get_channel(int(cid))

        if not channel:
            return

        try:
            await self.send_welcome(channel, member)
        except discord.HTTPException:
            pass


async def setup(bot):
    await bot.add_cog(Welcome(bot))
