import discord
from discord import app_commands
from discord.ext import commands


class JTC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = set()

    @app_commands.command(
        name="jtc_setup",
        description="Set the Join-to-Create voice channel"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def jtc_setup(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel
    ):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "jtc_channel",
            str(channel.id)
        )

        await interaction.response.send_message(
            f"✅ Join-to-Create enabled for {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(
        name="jtc_disable",
        description="Disable Join-to-Create"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def jtc_disable(self, interaction: discord.Interaction):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "jtc_channel",
            ""
        )

        await interaction.response.send_message(
            "✅ Join-to-Create disabled.",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):
        if member.bot:
            return

        guild = member.guild

        channel_id = await self.bot.db.setting(
            guild.id,
            "jtc_channel"
        )

        if not channel_id:
            return

        # Member joined the JTC channel
        if after.channel and str(after.channel.id) == str(channel_id):

            try:
                new_channel = await guild.create_voice_channel(
                    name=f"🔊 {member.display_name}'s Room",
                    category=after.channel.category
                )

                self.temp_channels.add(new_channel.id)

                await member.move_to(new_channel)

            except discord.Forbidden:
                return

        # Delete an empty temporary channel
        if before.channel and before.channel.id in self.temp_channels:

            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete(
                        reason="Empty temporary voice channel"
                    )

                    self.temp_channels.discard(
                        before.channel.id
                    )

                except discord.NotFound:
                    self.temp_channels.discard(
                        before.channel.id
                    )

                except discord.Forbidden:
                    pass


async def setup(bot):
    await bot.add_cog(JTC(bot))
