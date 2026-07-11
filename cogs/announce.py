import discord
from discord import app_commands
from discord.ext import commands


class Announce(commands.Cog):
    """リリース・コラボ告知用のテンプレート投稿コマンド"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="announce_release", description="新曲・新作のリリース告知をEmbedで投稿します")
    @app_commands.describe(
        title="曲名/作品名",
        url="視聴・DLリンク",
        note="コメント(任意)",
        image_url="ジャケット画像URL(任意)",
        mention_role="通知したいロール(任意)",
    )
    async def announce_release(
        self,
        interaction: discord.Interaction,
        title: str,
        url: str,
        note: str | None = None,
        image_url: str | None = None,
        mention_role: discord.Role | None = None,
    ) -> None:
        await self.do_release(interaction, title, url, note, image_url, mention_role)

    async def do_release(
        self,
        interaction: discord.Interaction,
        title: str,
        url: str,
        note: str | None = None,
        image_url: str | None = None,
        mention_role: discord.Role | None = None,
    ) -> None:
        embed = discord.Embed(
            title=f"🎵 New Release: {title}",
            url=url,
            description=note or "",
            color=discord.Color.gold(),
        )
        embed.add_field(name="リンク", value=url, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        if image_url:
            embed.set_image(url=image_url)

        content = mention_role.mention if mention_role else None
        await interaction.response.send_message(content=content, embed=embed)

    @app_commands.command(name="announce_collab", description="コラボ募集の告知をEmbedで投稿します")
    @app_commands.describe(
        title="企画タイトル",
        description="募集内容の説明",
        deadline="締め切り(任意、例: 2026/08/01)",
        mention_role="通知したいロール(任意)",
    )
    async def announce_collab(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        deadline: str | None = None,
        mention_role: discord.Role | None = None,
    ) -> None:
        await self.do_collab(interaction, title, description, deadline, mention_role)

    async def do_collab(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        deadline: str | None = None,
        mention_role: discord.Role | None = None,
    ) -> None:
        embed = discord.Embed(
            title=f"🤝 Collab: {title}",
            description=description,
            color=discord.Color.magenta(),
        )
        if deadline:
            embed.add_field(name="締め切り", value=deadline, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        content = mention_role.mention if mention_role else None
        await interaction.response.send_message(content=content, embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Announce(bot))
