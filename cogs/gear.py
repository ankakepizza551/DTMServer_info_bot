import discord
from discord import app_commands
from discord.ext import commands

from db import get_db

CATEGORY_CHOICES = ["DAW", "VST/Plugin", "Audio Interface", "MIDI Controller", "Monitor/Headphone", "Mic", "Other"]


class Gear(commands.Cog):
    """メンバーが使っているプラグイン/機材の情報共有DB"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="gear_add", description="使っているプラグイン/機材を登録します")
    @app_commands.describe(category="カテゴリ", name="製品名")
    @app_commands.choices(
        category=[app_commands.Choice(name=c, value=c) for c in CATEGORY_CHOICES]
    )
    async def gear_add(self, interaction: discord.Interaction, category: app_commands.Choice[str], name: str) -> None:
        db = get_db()
        await db.execute(
            "INSERT INTO gear (guild_id, user_id, category, name) VALUES (?, ?, ?, ?)",
            (interaction.guild_id, interaction.user.id, category.value, name),
        )
        await db.commit()
        await interaction.response.send_message(f"登録しました: **{category.value}** / {name}")

    @app_commands.command(name="gear_search", description="カテゴリや製品名でメンバーの機材を検索します")
    @app_commands.describe(keyword="カテゴリ名または製品名の一部")
    async def gear_search(self, interaction: discord.Interaction, keyword: str) -> None:
        db = get_db()
        like = f"%{keyword}%"
        cursor = await db.execute(
            "SELECT category, name, user_id FROM gear WHERE guild_id = ? "
            "AND (category LIKE ? OR name LIKE ?) ORDER BY id DESC LIMIT 25",
            (interaction.guild_id, like, like),
        )
        rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message(f"'{keyword}' に一致する機材は見つかりませんでした。", ephemeral=True)
            return

        lines = [f"**{category}** / {name} - <@{user_id}>" for category, name, user_id in rows]

        embed = discord.Embed(
            title=f"'{keyword}' の検索結果",
            description="\n".join(lines),
            color=discord.Color.dark_teal(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gear_list", description="メンバーが登録した機材一覧を表示します")
    @app_commands.describe(member="表示するメンバー(未指定なら自分)")
    async def gear_list(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        target = member or interaction.user
        db = get_db()
        cursor = await db.execute(
            "SELECT category, name FROM gear WHERE guild_id = ? AND user_id = ? ORDER BY category, id",
            (interaction.guild_id, target.id),
        )
        rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message(f"{target.display_name} はまだ機材を登録していません。", ephemeral=True)
            return

        lines = [f"**{category}** / {name}" for category, name in rows]

        embed = discord.Embed(
            title=f"{target.display_name} の登録機材",
            description="\n".join(lines),
            color=discord.Color.dark_teal(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Gear(bot))
