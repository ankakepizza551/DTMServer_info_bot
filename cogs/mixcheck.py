import discord
from discord import app_commands
from discord.ext import commands

from db import get_db

DONE_EMOJI = "✅"


class MixCheck(commands.Cog):
    """ミックスチェック依頼のキュー管理"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="mixcheck_submit", description="ミックスチェックを依頼します")
    @app_commands.describe(url="音源のURL", note="確認してほしいポイントなど(任意)")
    async def mixcheck_submit(self, interaction: discord.Interaction, url: str, note: str | None = None) -> None:
        await self.do_submit(interaction, url, note)

    async def do_submit(self, interaction: discord.Interaction, url: str, note: str | None = None) -> None:
        embed = discord.Embed(
            title="🎚️ ミックスチェック依頼",
            description=note or "",
            color=discord.Color.red(),
        )
        embed.add_field(name="音源", value=url, inline=False)
        embed.add_field(name="ステータス", value="⏳ レビュー待ち", inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"レビューが完了したら{DONE_EMOJI}をリアクションしてください")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction(DONE_EMOJI)

        db = get_db()
        await db.execute(
            "INSERT INTO mix_requests (guild_id, channel_id, message_id, user_id, url, note) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (interaction.guild_id, interaction.channel_id, message.id, interaction.user.id, url, note),
        )
        await db.commit()

    @app_commands.command(name="mixcheck_queue", description="レビュー待ちのミックスチェック一覧を表示します")
    async def mixcheck_queue(self, interaction: discord.Interaction) -> None:
        await self.do_queue(interaction)

    async def do_queue(self, interaction: discord.Interaction) -> None:
        db = get_db()
        cursor = await db.execute(
            "SELECT url, user_id, channel_id, message_id, created_at FROM mix_requests "
            "WHERE guild_id = ? AND status = 'pending' ORDER BY id",
            (interaction.guild_id,),
        )
        rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("レビュー待ちのミックスはありません。", ephemeral=True)
            return

        lines = []
        for url, user_id, channel_id, message_id, created_at in rows:
            jump_url = f"https://discord.com/channels/{interaction.guild_id}/{channel_id}/{message_id}"
            lines.append(f"[{url}]({jump_url}) - <@{user_id}> ({created_at} UTC)")

        embed = discord.Embed(
            title="ミックスチェック待ちキュー",
            description="\n".join(lines),
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if str(payload.emoji) != DONE_EMOJI or payload.guild_id is None or payload.member is None:
            return
        if payload.member.bot:
            return

        db = get_db()
        cursor = await db.execute(
            "SELECT id, user_id, status FROM mix_requests WHERE message_id = ? AND guild_id = ?",
            (payload.message_id, payload.guild_id),
        )
        row = await cursor.fetchone()
        if row is None:
            return

        request_id, submitter_id, status = row
        if status != "pending" or payload.member.id == submitter_id:
            return

        await db.execute("UPDATE mix_requests SET status = 'done' WHERE id = ?", (request_id,))
        await db.commit()

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        if message.embeds:
            embed = message.embeds[0]
            embed.color = discord.Color.green()
            embed.set_field_at(1, name="ステータス", value=f"✅ レビュー完了 (by {payload.member.display_name})", inline=False)
            await message.edit(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MixCheck(bot))
