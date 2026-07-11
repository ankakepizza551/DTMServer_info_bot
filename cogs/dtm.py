import discord
from discord import app_commands
from discord.ext import commands

from theory import NOTE_NAMES, parse_note

SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "major_pentatonic": [0, 2, 4, 7, 9],
}

# note division -> beats(4分音符=1拍)換算した拍数
NOTE_DIVISIONS = {
    "1/1": 4.0,
    "1/2": 2.0,
    "1/2.": 3.0,
    "1/2t": 4.0 / 3,
    "1/4": 1.0,
    "1/4.": 1.5,
    "1/4t": 2.0 / 3,
    "1/8": 0.5,
    "1/8.": 0.75,
    "1/8t": 1.0 / 3,
    "1/16": 0.25,
    "1/16.": 0.375,
    "1/16t": 1.0 / 6,
    "1/32": 0.125,
}


class DTM(commands.Cog):
    """DTM(音楽制作)向けの計算・補助コマンド"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="bpmdelay", description="BPMからディレイ/LFOに使えるms換算表を表示します")
    @app_commands.describe(bpm="曲のBPM (例: 128)")
    async def bpmdelay(self, interaction: discord.Interaction, bpm: float) -> None:
        await self.do_bpmdelay(interaction, bpm)

    async def do_bpmdelay(self, interaction: discord.Interaction, bpm: float) -> None:
        if bpm <= 0:
            await interaction.response.send_message("BPMは正の数で指定してください。", ephemeral=True)
            return

        quarter_note_ms = 60000.0 / bpm
        lines = [f"`{name:>6}` : {quarter_note_ms * beats:7.1f} ms" for name, beats in NOTE_DIVISIONS.items()]

        embed = discord.Embed(
            title=f"BPM {bpm:g} のディレイ/LFOタイム換算表",
            description="\n".join(lines),
            color=discord.Color.green(),
        )
        embed.set_footer(text="t=3連符 / .=付点")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="scale", description="指定したキー・スケールの構成音を表示します")
    @app_commands.describe(root="ルート音 (例: C, F#, Bb)", scale="スケールの種類")
    @app_commands.choices(
        scale=[app_commands.Choice(name=name.replace("_", " "), value=name) for name in SCALE_INTERVALS]
    )
    async def scale(self, interaction: discord.Interaction, root: str, scale: app_commands.Choice[str]) -> None:
        await self.do_scale(interaction, root, scale.value)

    async def do_scale(self, interaction: discord.Interaction, root: str, scale_key: str) -> None:
        root_index = parse_note(root)
        if root_index is None:
            await interaction.response.send_message(
                f"'{root}' はルート音として認識できませんでした。例: C, D#, Bb", ephemeral=True
            )
            return

        if scale_key not in SCALE_INTERVALS:
            await interaction.response.send_message(
                f"'{scale_key}' はスケール名として認識できませんでした。使えるのは: "
                f"`{'`, `'.join(SCALE_INTERVALS)}`",
                ephemeral=True,
            )
            return

        intervals = SCALE_INTERVALS[scale_key]
        notes = [NOTE_NAMES[(root_index + interval) % 12] for interval in intervals]

        embed = discord.Embed(
            title=f"{NOTE_NAMES[root_index]} {scale_key.replace('_', ' ')}",
            description=" - ".join(notes),
            color=discord.Color.orange(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DTM(bot))
