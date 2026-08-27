import discord
from discord import app_commands
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    async def connect(self, interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Join a voice channel first.", ephemeral=True)
            return None
        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()
        return vc

    @app_commands.command(name="play", description="Play a URL or search query (requires FFmpeg/yt-dlp)")
    async def play(self, interaction, query: str):
        await interaction.response.send_message(
            "🎵 Music module is scaffolded. Install/configure FFmpeg + yt-dlp on Railway, then this command can be connected to your preferred audio source.",
            ephemeral=True
        )

    @app_commands.command(name="pause", description="Pause music")
    async def pause(self, interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Paused.")
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @app_commands.command(name="resume", description="Resume music")
    async def resume(self, interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Resumed.")
        else:
            await interaction.response.send_message("Nothing is paused.", ephemeral=True)

    @app_commands.command(name="skip", description="Skip current music")
    async def skip(self, interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped.")
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @app_commands.command(name="queue", description="Show music queue")
    async def queue(self, interaction):
        await interaction.response.send_message("🎵 Queue is empty.", ephemeral=True)

    @app_commands.command(name="stop", description="Stop music and leave voice")
    async def stop(self, interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⏹️ Stopped.")
        else:
            await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))
