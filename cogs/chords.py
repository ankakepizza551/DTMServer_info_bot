import random

import discord
from discord import app_commands
from discord.ext import commands

from theory import (
    MAJOR_DEGREE_QUALITIES,
    MAJOR_SCALE_INTERVALS,
    NATURAL_MINOR_DEGREE_QUALITIES,
    NATURAL_MINOR_SCALE_INTERVALS,
    NOTE_NAMES,
    parse_note,
)

# ローマ数字表記(度数)で定義した定番進行
MAJOR_PROGRESSIONS = {
    "王道進行 (IV-V-iii-vi)": [4, 5, 3, 6],
    "カノン進行 (I-V-vi-iii-IV-I-IV-V)": [1, 5, 6, 3, 4, 1, 4, 5],
    "I-V-vi-IV": [1, 5, 6, 4],
    "I-IV-V": [1, 4, 5],
    "ii-V-I": [2, 5, 1],
    "I-vi-IV-V": [1, 6, 4, 5],
    "vi-IV-I-V": [6, 4, 1, 5],
}

MINOR_PROGRESSIONS = {
    "小室進行 (VI-VII-i-V)": [6, 7, 1, 5],
    "i-VI-III-VII": [1, 6, 3, 7],
    "i-iv-v": [1, 4, 5],
    "i-VII-VI-VII": [1, 7, 6, 7],
    "i-iv-VII-III": [1, 4, 7, 3],
}


def build_chord_name(root_index: int, key_root_index: int, intervals: list[int], qualities: list[str], degree: int) -> str:
    scale_index = (degree - 1) % 7
    note_index = (key_root_index + intervals[scale_index]) % 12
    return f"{NOTE_NAMES[note_index]}{qualities[scale_index]}"


class Chords(commands.Cog):
    """コード進行の提案コマンド"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="chords", description="指定したキーの定番コード進行を提案します")
    @app_commands.describe(root="キーのルート音 (例: C, F#, Bb)", mode="メジャー/マイナー")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Major", value="major"),
            app_commands.Choice(name="Minor", value="minor"),
        ]
    )
    async def chords(self, interaction: discord.Interaction, root: str, mode: app_commands.Choice[str]) -> None:
        await self.do_chords(interaction, root, mode.value)

    async def do_chords(self, interaction: discord.Interaction, root: str, mode_value: str) -> None:
        root_index = parse_note(root)
        if root_index is None:
            await interaction.response.send_message(
                f"'{root}' はルート音として認識できませんでした。例: C, D#, Bb", ephemeral=True
            )
            return

        if mode_value not in ("major", "minor"):
            await interaction.response.send_message(
                "モードは `major` か `minor` で指定してください。", ephemeral=True
            )
            return

        if mode_value == "major":
            intervals, qualities, progressions = MAJOR_SCALE_INTERVALS, MAJOR_DEGREE_QUALITIES, MAJOR_PROGRESSIONS
        else:
            intervals, qualities, progressions = (
                NATURAL_MINOR_SCALE_INTERVALS,
                NATURAL_MINOR_DEGREE_QUALITIES,
                MINOR_PROGRESSIONS,
            )

        lines = []
        for name, degrees in progressions.items():
            chord_names = [build_chord_name(root_index, root_index, intervals, qualities, d) for d in degrees]
            lines.append(f"**{name}**\n{' - '.join(chord_names)}")

        embed = discord.Embed(
            title=f"{NOTE_NAMES[root_index]} {mode_value.capitalize()} の定番コード進行",
            description="\n\n".join(lines),
            color=discord.Color.purple(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="chordrandom", description="指定したキーからランダムに1つコード進行を提案します")
    @app_commands.describe(root="キーのルート音 (例: C, F#, Bb)", mode="メジャー/マイナー")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Major", value="major"),
            app_commands.Choice(name="Minor", value="minor"),
        ]
    )
    async def chordrandom(self, interaction: discord.Interaction, root: str, mode: app_commands.Choice[str]) -> None:
        await self.do_chordrandom(interaction, root, mode.value)

    async def do_chordrandom(self, interaction: discord.Interaction, root: str, mode_value: str) -> None:
        root_index = parse_note(root)
        if root_index is None:
            await interaction.response.send_message(
                f"'{root}' はルート音として認識できませんでした。例: C, D#, Bb", ephemeral=True
            )
            return

        if mode_value not in ("major", "minor"):
            await interaction.response.send_message(
                "モードは `major` か `minor` で指定してください。", ephemeral=True
            )
            return

        if mode_value == "major":
            intervals, qualities, progressions = MAJOR_SCALE_INTERVALS, MAJOR_DEGREE_QUALITIES, MAJOR_PROGRESSIONS
        else:
            intervals, qualities, progressions = (
                NATURAL_MINOR_SCALE_INTERVALS,
                NATURAL_MINOR_DEGREE_QUALITIES,
                MINOR_PROGRESSIONS,
            )

        name, degrees = random.choice(list(progressions.items()))
        chord_names = [build_chord_name(root_index, root_index, intervals, qualities, d) for d in degrees]

        embed = discord.Embed(
            title=f"{NOTE_NAMES[root_index]} {mode_value.capitalize()} - {name}",
            description=" - ".join(chord_names),
            color=discord.Color.purple(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chords(bot))
