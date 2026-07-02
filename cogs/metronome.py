import asyncio
import math
import struct
import wave
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

CLICK_PATH = Path(__file__).parent.parent / "data" / "click.wav"


def ensure_click_file() -> None:
    """クリック音(短いサイン波バースト)のWAVファイルを1回だけ生成する"""
    if CLICK_PATH.exists():
        return

    CLICK_PATH.parent.mkdir(parents=True, exist_ok=True)

    sample_rate = 44100
    duration_sec = 0.05
    freq = 1500.0
    n_samples = int(sample_rate * duration_sec)

    frames = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        envelope = 1.0 - (i / n_samples)  # 減衰させてクリック感を出す
        sample = math.sin(2 * math.pi * freq * t) * envelope
        frames += struct.pack("<h", int(sample * 32767 * 0.8))

    with wave.open(str(CLICK_PATH), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))


class Metronome(commands.Cog):
    """ボイスチャンネルでBPMに合わせたクリック音を再生する"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._tasks: dict[int, asyncio.Task] = {}
        ensure_click_file()

    def cog_unload(self) -> None:
        for task in self._tasks.values():
            task.cancel()

    async def _click_loop(self, voice_client: discord.VoiceClient, bpm: float) -> None:
        interval = 60.0 / bpm
        try:
            while True:
                if voice_client.is_connected():
                    if not voice_client.is_playing():
                        voice_client.play(discord.FFmpegPCMAudio(str(CLICK_PATH)))
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    @app_commands.command(name="metronome_start", description="ボイスチャンネルでメトロノームを再生します")
    @app_commands.describe(bpm="再生するBPM (例: 120)")
    async def metronome_start(self, interaction: discord.Interaction, bpm: float) -> None:
        if not (20 <= bpm <= 300):
            await interaction.response.send_message("BPMは20〜300の範囲で指定してください。", ephemeral=True)
            return

        member = interaction.user
        if not isinstance(member, discord.Member) or member.voice is None or member.voice.channel is None:
            await interaction.response.send_message("先にボイスチャンネルに参加してください。", ephemeral=True)
            return

        guild_id = interaction.guild_id
        if guild_id in self._tasks:
            await interaction.response.send_message(
                "既にメトロノームが再生中です。`/metronome_stop`で停止してから再度実行してください。", ephemeral=True
            )
            return

        voice_channel = member.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        task = self.bot.loop.create_task(self._click_loop(voice_client, bpm))
        self._tasks[guild_id] = task

        await interaction.response.send_message(f"BPM {bpm:g} でメトロノームを開始しました。")

    @app_commands.command(name="metronome_stop", description="メトロノームを停止してボイスチャンネルから退出します")
    async def metronome_stop(self, interaction: discord.Interaction) -> None:
        guild_id = interaction.guild_id
        task = self._tasks.pop(guild_id, None)
        if task is not None:
            task.cancel()

        voice_client = interaction.guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect()

        if task is None and voice_client is None:
            await interaction.response.send_message("メトロノームは再生されていません。", ephemeral=True)
            return

        await interaction.response.send_message("メトロノームを停止しました。")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Metronome(bot))
