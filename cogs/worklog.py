import discord
from discord import app_commands
from discord.ext import commands

from db import get_db


class WorkLog(commands.Cog):
    """作業ログ・進捗管理コマンド"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="log", description="今日やった作業を記録します")
    @app_commands.describe(content="作業内容")
    async def log(self, interaction: discord.Interaction, content: str) -> None:
        db = get_db()
        await db.execute(
            "INSERT INTO work_logs (guild_id, user_id, content) VALUES (?, ?, ?)",
            (interaction.guild_id, interaction.user.id, content),
        )
        await db.commit()
        await interaction.response.send_message(f"記録しました: {content}")

    @app_commands.command(name="worklog", description="直近の作業ログを表示します")
    @app_commands.describe(member="表示するメンバー(未指定なら自分)", count="表示件数(デフォルト10、最大25)")
    async def worklog(
        self, interaction: discord.Interaction, member: discord.Member | None = None, count: int = 10
    ) -> None:
        target = member or interaction.user
        count = max(1, min(count, 25))

        db = get_db()
        cursor = await db.execute(
            "SELECT content, created_at FROM work_logs WHERE guild_id = ? AND user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (interaction.guild_id, target.id, count),
        )
        rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message(f"{target.display_name} の作業ログはまだありません。", ephemeral=True)
            return

        lines = [f"`{created_at} UTC` {content}" for content, created_at in rows]

        embed = discord.Embed(
            title=f"{target.display_name} の作業ログ",
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorkLog(bot))
