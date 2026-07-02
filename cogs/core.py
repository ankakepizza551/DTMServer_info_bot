import discord
from discord import app_commands
from discord.ext import commands


class Core(commands.Cog):
    """基本コマンド: 疎通確認・サーバー情報表示"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Botの応答速度を確認します")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! `{latency_ms}ms`")

    @app_commands.command(name="serverinfo", description="このサーバーの情報を表示します")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        online = sum(1 for m in guild.members if m.status != discord.Status.offline)

        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="メンバー数", value=str(guild.member_count), inline=True)
        embed.add_field(name="オンライン", value=str(online), inline=True)
        embed.add_field(name="ロール数", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="チャンネル数", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="作成日", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True)
        if guild.owner:
            embed.add_field(name="オーナー", value=guild.owner.mention, inline=True)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Core(bot))
