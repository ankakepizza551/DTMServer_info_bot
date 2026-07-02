import discord
from discord import app_commands
from discord.ext import commands

from db import get_db

PROJECT_EXTENSIONS = {
    ".flp",  # FL Studio
    ".als",  # Ableton Live
    ".logicx",  # Logic Pro (フォルダだがzip添付されることが多い)
    ".rpp", ".rpp-bak",  # Reaper
    ".ptx", ".ptf",  # Pro Tools
    ".cpr",  # Cubase
    ".song",  # Studio One
    ".dawproject",
    ".zip", ".7z", ".rar",  # 圧縮されたプロジェクト一式
}


class Projects(commands.Cog):
    """DAWプロジェクトファイルの置き場を自動で記録・一覧化する"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None or not message.attachments:
            return

        db = get_db()
        matched = False
        for attachment in message.attachments:
            filename_lower = attachment.filename.lower()
            if any(filename_lower.endswith(ext) for ext in PROJECT_EXTENSIONS):
                matched = True
                await db.execute(
                    "INSERT INTO projects (guild_id, channel_id, message_id, user_id, filename, url) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        message.guild.id,
                        message.channel.id,
                        message.id,
                        message.author.id,
                        attachment.filename,
                        attachment.url,
                    ),
                )
        if matched:
            await db.commit()
            try:
                await message.add_reaction("📁")
            except discord.HTTPException:
                pass

    @app_commands.command(name="projects", description="最近共有されたDAWプロジェクトファイルの一覧を表示します")
    @app_commands.describe(count="表示件数(デフォルト10、最大25)")
    async def projects(self, interaction: discord.Interaction, count: int = 10) -> None:
        count = max(1, min(count, 25))
        db = get_db()
        cursor = await db.execute(
            "SELECT filename, url, user_id, created_at FROM projects WHERE guild_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (interaction.guild_id, count),
        )
        rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("まだプロジェクトファイルが記録されていません。", ephemeral=True)
            return

        lines = [f"[{filename}]({url}) - <@{user_id}> ({created_at} UTC)" for filename, url, user_id, created_at in rows]

        embed = discord.Embed(
            title="最近のプロジェクトファイル",
            description="\n".join(lines),
            color=discord.Color.teal(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Projects(bot))
