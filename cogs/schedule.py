import discord
from discord import app_commands
from discord.ext import commands

AVAILABILITY_EMOJIS = ["⭕", "❌", "❔"]  # 参加可能 / 不可 / 未定


class Schedule(commands.Cog):
    """練習/セッションの日程調整用リアクション投票"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="session_propose", description="練習/セッションの日程を提案し、リアクションで参加可否を集めます")
    @app_commands.describe(date="候補日時(例: 2026/07/10 21:00)", note="内容・メモ(任意)")
    async def session_propose(self, interaction: discord.Interaction, date: str, note: str | None = None) -> None:
        await self.do_propose(interaction, date, note)

    async def do_propose(self, interaction: discord.Interaction, date: str, note: str | None = None) -> None:
        embed = discord.Embed(
            title="🗓️ セッション日程調整",
            description=note or "",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="候補日時", value=date, inline=False)
        embed.add_field(
            name="回答方法",
            value=f"{AVAILABILITY_EMOJIS[0]} 参加可能 / {AVAILABILITY_EMOJIS[1]} 不可 / {AVAILABILITY_EMOJIS[2]} 未定",
            inline=False,
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        for emoji in AVAILABILITY_EMOJIS:
            await message.add_reaction(emoji)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Schedule(bot))
