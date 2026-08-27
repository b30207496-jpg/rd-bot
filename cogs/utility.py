import asyncio
import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Show a user's avatar")
    async def avatar(self, interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Avatar")
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show user information")
    async def userinfo(self, interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title="👤 User Info", color=discord.Color.blurple())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, "F"))
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, "F"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Show server information")
    async def serverinfo(self, interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
        embed.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        embed.add_field(name="Owner", value=f"<@{g.owner_id}>")
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Channels", value=str(len(g.channels)))
        embed.add_field(name="Roles", value=str(len(g.roles)))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind", description="Set a simple reminder")
    async def remind(self, interaction, minutes: app_commands.Range[int, 1, 10080], text: str):
        await interaction.response.send_message(f"⏰ Reminder set for {minutes} minute(s).", ephemeral=True)
        await asyncio.sleep(minutes * 60)
        try:
            await interaction.user.send(f"⏰ Reminder: {text}")
        except discord.HTTPException:
            pass

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction, text: str):
        await interaction.response.send_message(text)
        try:
            await interaction.delete_original_response()
        except discord.HTTPException:
            pass

    @app_commands.command(name="afk", description="Set your AFK message")
    async def afk(self, interaction, message: str = "AFK"):
        await self.bot.db.set_setting(interaction.guild.id, f"afk:{interaction.user.id}", message)
        await interaction.response.send_message(f"💤 AFK set: {message}")

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"🏓 Pong! **{latency}ms**"
        )

    @app_commands.command(name="botinfo", description="Show bot information")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Bot",
            value=str(self.bot.user),
            inline=True
        )
        embed.add_field(
            name="Servers",
            value=str(len(self.bot.guilds)),
            inline=True
        )
        embed.add_field(
            name="Commands",
            value=str(len(self.bot.tree.get_commands())),
            inline=True
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roleinfo", description="Show role information")
    async def roleinfo(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        embed = discord.Embed(
            title=f"🎭 Role Info — {role.name}",
            color=role.color
        )

        embed.add_field(name="ID", value=str(role.id))
        embed.add_field(name="Members", value=str(len(role.members)))
        embed.add_field(name="Position", value=str(role.position))
        embed.add_field(name="Mentionable", value=str(role.mentionable))

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="channelinfo",
        description="Show channel information"
    )
    async def channelinfo(self, interaction: discord.Interaction):
        channel = interaction.channel

        embed = discord.Embed(
            title=f"📺 Channel Info — {channel.name}",
            color=discord.Color.blurple()
        )

        embed.add_field(name="ID", value=str(channel.id))
        embed.add_field(name="Type", value=str(channel.type))

        if hasattr(channel, "category") and channel.category:
            embed.add_field(
                name="Category",
                value=channel.category.name
            )

        await interaction.response.send_message(embed=embed)
async def setup(bot):
    await bot.add_cog(Utility(bot))
