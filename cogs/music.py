import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp


YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.current = {}

    async def connect(self, interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Join a voice channel first.",
                ephemeral=True
            )
            return None

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc is None:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        return vc

    async def extract(self, query):
        loop = asyncio.get_running_loop()

        def get_info():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(query, download=False)

                if "entries" in info:
                    info = info["entries"][0]

                return {
                    "title": info.get("title", "Unknown"),
                    "url": info["url"],
                    "webpage": info.get("webpage_url", query),
                }

        return await loop.run_in_executor(None, get_info)

    async def play_next(self, guild_id):
        queue = self.queues.get(guild_id, [])

        if not queue:
            self.current.pop(guild_id, None)
            return

        song = queue.pop(0)
        self.current[guild_id] = song

        guild = self.bot.get_guild(guild_id)

        if not guild:
            return

        vc = guild.voice_client

        if not vc:
            return

        try:
            source = discord.FFmpegPCMAudio(
                song["url"],
                **FFMPEG_OPTIONS
            )

            def after(error):
                if error:
                    print(f"Music playback error: {error}")

                asyncio.run_coroutine_threadsafe(
                    self.play_next(guild_id),
                    self.bot.loop
                )

            vc.play(source, after=after)

        except Exception as e:
            print(f"Could not play music: {e}")
            await self.play_next(guild_id)

    @app_commands.command(
        name="play",
        description="Play a song from YouTube"
    )
    @app_commands.describe(
        query="Song name or YouTube URL"
    )
    async def play(self, interaction, query: str):
        vc = await self.connect(interaction)

        if not vc:
            return

        await interaction.response.defer()

        try:
            song = await self.extract(query)

            guild_id = interaction.guild.id

            if guild_id not in self.queues:
                self.queues[guild_id] = []

            if vc.is_playing() or vc.is_paused():
                self.queues[guild_id].append(song)

                await interaction.followup.send(
                    f"🎵 Added to queue: **{song['title']}**"
                )
            else:
                self.queues[guild_id].append(song)

                await interaction.followup.send(
                    f"🎶 Now playing: **{song['title']}**"
                )

                await self.play_next(guild_id)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Could not play that song.\n`{e}`"
            )

    @app_commands.command(
        name="pause",
        description="Pause the current music"
    )
    async def pause(self, interaction):
        vc = interaction.guild.voice_client

        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message(
                "⏸️ Paused."
            )
        else:
            await interaction.response.send_message(
                "❌ Nothing is playing.",
                ephemeral=True
            )

    @app_commands.command(
        name="resume",
        description="Resume paused music"
    )
    async def resume(self, interaction):
        vc = interaction.guild.voice_client

        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message(
                "▶️ Resumed."
            )
        else:
            await interaction.response.send_message(
                "❌ Nothing is paused.",
                ephemeral=True
            )

    @app_commands.command(
        name="skip",
        description="Skip the current song"
    )
    async def skip(self, interaction):
        vc = interaction.guild.voice_client

        if vc and vc.is_playing():
            vc.stop()

            await interaction.response.send_message(
                "⏭️ Skipped."
            )
        else:
            await interaction.response.send_message(
                "❌ Nothing is playing.",
                ephemeral=True
            )

    @app_commands.command(
        name="queue",
        description="Show the music queue"
    )
    async def queue(self, interaction):
        guild_id = interaction.guild.id
        queue = self.queues.get(guild_id, [])
        current = self.current.get(guild_id)

        lines = []

        if current:
            lines.append(
                f"🎶 **Now playing:** {current['title']}"
            )

        if queue:
            lines.append("\n📜 **Up next:**")

            for i, song in enumerate(queue[:10], start=1):
                lines.append(
                    f"`{i}.` {song['title']}"
                )

        if not lines:
            await interaction.response.send_message(
                "🎵 Queue is empty.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "\n".join(lines)
        )

    @app_commands.command(
        name="stop",
        description="Stop music and leave the voice channel"
    )
    async def stop(self, interaction):
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client

        self.queues[guild_id] = []
        self.current.pop(guild_id, None)

        if vc:
            vc.stop()
            await vc.disconnect()

            await interaction.response.send_message(
                "⏹️ Music stopped and I left the voice channel."
            )
        else:
            await interaction.response.send_message(
                "❌ I'm not in a voice channel.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Music(bot))  
