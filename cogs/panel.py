import discord
from discord import app_commands
from discord.ext import commands


# ─────────────────────────────────────────────
#  入力が必要なコマンド用のモーダル
# ─────────────────────────────────────────────

class BpmDelayModal(discord.ui.Modal, title="🥁 BPM ディレイ換算表"):
    bpm = discord.ui.TextInput(label="BPM", placeholder="例: 128", max_length=6)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            bpm_value = float(self.bpm.value)
        except ValueError:
            await interaction.response.send_message("BPMは数値で入力してください。", ephemeral=True)
            return
        await self.bot.get_cog("DTM").do_bpmdelay(interaction, bpm_value)


class ScaleModal(discord.ui.Modal, title="🎼 スケール表示"):
    root = discord.ui.TextInput(label="ルート音", placeholder="例: C, F#, Bb", max_length=3)
    scale = discord.ui.TextInput(
        label="スケール",
        placeholder="major / minor / dorian / phrygian / lydian / mixolydian / locrian / major_pentatonic / minor_pentatonic",
        max_length=30,
    )

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("DTM").do_scale(interaction, self.root.value, self.scale.value.strip().lower())


class ChordsModal(discord.ui.Modal, title="🎹 定番コード進行"):
    root = discord.ui.TextInput(label="キーのルート音", placeholder="例: C, F#, Bb", max_length=3)
    mode = discord.ui.TextInput(label="メジャー/マイナー", placeholder="major または minor", max_length=10)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Chords").do_chords(interaction, self.root.value, self.mode.value.strip().lower())


class ChordRandomModal(discord.ui.Modal, title="🎲 コード進行をランダム提案"):
    root = discord.ui.TextInput(label="キーのルート音", placeholder="例: C, F#, Bb", max_length=3)
    mode = discord.ui.TextInput(label="メジャー/マイナー", placeholder="major または minor", max_length=10)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Chords").do_chordrandom(interaction, self.root.value, self.mode.value.strip().lower())


class MetronomeStartModal(discord.ui.Modal, title="🎵 メトロノーム開始"):
    bpm = discord.ui.TextInput(label="BPM (20〜300)", placeholder="例: 120", max_length=3)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            bpm_value = float(self.bpm.value)
        except ValueError:
            await interaction.response.send_message("BPMは数値で入力してください。", ephemeral=True)
            return
        await self.bot.get_cog("Metronome").do_start(interaction, bpm_value)


class LogModal(discord.ui.Modal, title="📝 作業ログを記録"):
    content = discord.ui.TextInput(
        label="今日やった作業", style=discord.TextStyle.paragraph, max_length=300
    )

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("WorkLog").do_log(interaction, self.content.value)


class GearAddModal(discord.ui.Modal, title="🎛️ 機材/プラグインを登録"):
    category = discord.ui.TextInput(
        label="カテゴリ",
        placeholder="DAW / VST/Plugin / Audio Interface / MIDI Controller / Monitor/Headphone / Mic / Other",
        max_length=30,
    )
    name = discord.ui.TextInput(label="製品名", max_length=100)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Gear").do_gear_add(interaction, self.category.value.strip(), self.name.value.strip())


class GearSearchModal(discord.ui.Modal, title="🔍 機材を検索"):
    keyword = discord.ui.TextInput(label="カテゴリ名または製品名の一部", max_length=100)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Gear").do_gear_search(interaction, self.keyword.value.strip())


class MixCheckSubmitModal(discord.ui.Modal, title="🎚️ ミックスチェック依頼"):
    url = discord.ui.TextInput(label="音源のURL", max_length=300)
    note = discord.ui.TextInput(
        label="確認してほしいポイント(任意)", style=discord.TextStyle.paragraph, required=False, max_length=300
    )

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        note_value = self.note.value.strip() or None
        await self.bot.get_cog("MixCheck").do_submit(interaction, self.url.value.strip(), note_value)


class AnnounceReleaseModal(discord.ui.Modal, title="🎵 リリース告知"):
    release_title = discord.ui.TextInput(label="曲名/作品名", max_length=100)
    url = discord.ui.TextInput(label="視聴・DLリンク", max_length=300)
    note = discord.ui.TextInput(
        label="コメント(任意)", style=discord.TextStyle.paragraph, required=False, max_length=300
    )
    image_url = discord.ui.TextInput(label="ジャケット画像URL(任意)", required=False, max_length=300)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Announce").do_release(
            interaction,
            self.release_title.value.strip(),
            self.url.value.strip(),
            self.note.value.strip() or None,
            self.image_url.value.strip() or None,
            None,
        )


class AnnounceCollabModal(discord.ui.Modal, title="🤝 コラボ募集告知"):
    collab_title = discord.ui.TextInput(label="企画タイトル", max_length=100)
    description = discord.ui.TextInput(
        label="募集内容の説明", style=discord.TextStyle.paragraph, max_length=500
    )
    deadline = discord.ui.TextInput(label="締め切り(任意、例: 2026/08/01)", required=False, max_length=50)

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Announce").do_collab(
            interaction,
            self.collab_title.value.strip(),
            self.description.value.strip(),
            self.deadline.value.strip() or None,
            None,
        )


class SessionProposeModal(discord.ui.Modal, title="🗓️ セッション日程調整"):
    date = discord.ui.TextInput(label="候補日時", placeholder="例: 2026/07/10 21:00", max_length=50)
    note = discord.ui.TextInput(
        label="内容・メモ(任意)", style=discord.TextStyle.paragraph, required=False, max_length=300
    )

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await self.bot.get_cog("Schedule").do_propose(interaction, self.date.value.strip(), self.note.value.strip() or None)


# ─────────────────────────────────────────────
#  入力不要(引数なし/自分固定)で即実行できるコマンド
# ─────────────────────────────────────────────

async def _run_direct(bot: commands.Bot, interaction: discord.Interaction, value: str) -> None:
    if value == "ping":
        await bot.get_cog("Core").do_ping(interaction)
    elif value == "serverinfo":
        await bot.get_cog("Core").do_serverinfo(interaction)
    elif value == "metronome_stop":
        await bot.get_cog("Metronome").do_stop(interaction)
    elif value == "projects":
        await bot.get_cog("Projects").do_projects(interaction)
    elif value == "worklog":
        await bot.get_cog("WorkLog").do_worklog(interaction)
    elif value == "gear_list":
        await bot.get_cog("Gear").do_gear_list(interaction)
    elif value == "mixcheck_queue":
        await bot.get_cog("MixCheck").do_queue(interaction)


MODAL_FACTORIES = {
    "bpmdelay": BpmDelayModal,
    "scale": ScaleModal,
    "chords": ChordsModal,
    "chordrandom": ChordRandomModal,
    "metronome_start": MetronomeStartModal,
    "log": LogModal,
    "gear_add": GearAddModal,
    "gear_search": GearSearchModal,
    "mixcheck_submit": MixCheckSubmitModal,
    "announce_release": AnnounceReleaseModal,
    "announce_collab": AnnounceCollabModal,
    "session_propose": SessionProposeModal,
}

DIRECT_VALUES = {
    "ping", "serverinfo", "metronome_stop", "projects", "worklog", "gear_list", "mixcheck_queue",
}


async def _dispatch(bot: commands.Bot, interaction: discord.Interaction, value: str) -> None:
    if value in MODAL_FACTORIES:
        await interaction.response.send_modal(MODAL_FACTORIES[value](bot))
    elif value in DIRECT_VALUES:
        await _run_direct(bot, interaction, value)


# ─────────────────────────────────────────────
#  カテゴリ別リストボックス(常設操作パネル)
# ─────────────────────────────────────────────

class BasicSelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(label="疎通確認 (ping)", value="ping", emoji="📶", description="Botの応答速度を確認"),
            discord.SelectOption(label="サーバー情報", value="serverinfo", emoji="ℹ️", description="メンバー数/ロール数などを表示"),
        ]
        super().__init__(
            placeholder="🔧 基本コマンド",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dtm_panel:basic",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await _dispatch(interaction.client, interaction, self.values[0])


class TheorySelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(label="BPMディレイ換算表", value="bpmdelay", emoji="🥁", description="BPMからディレイ/LFO用のms換算表"),
            discord.SelectOption(label="スケール表示", value="scale", emoji="🎼", description="キー・スケールの構成音を表示"),
            discord.SelectOption(label="定番コード進行", value="chords", emoji="🎹", description="王道進行/カノン進行など一覧"),
            discord.SelectOption(label="コード進行おまかせ", value="chordrandom", emoji="🎲", description="定番進行からランダムに1つ提案"),
            discord.SelectOption(label="メトロノーム開始", value="metronome_start", emoji="▶️", description="VCでクリック音を再生"),
            discord.SelectOption(label="メトロノーム停止", value="metronome_stop", emoji="⏹️", description="再生を停止してVC退出"),
        ]
        super().__init__(
            placeholder="🎵 音楽制作補助",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dtm_panel:theory",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await _dispatch(interaction.client, interaction, self.values[0])


class ProgressSelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(label="プロジェクト一覧", value="projects", emoji="📁", description="共有されたDAWプロジェクトファイル一覧(自分の直近分)"),
            discord.SelectOption(label="作業ログを記録", value="log", emoji="📝", description="今日やった作業を記録"),
            discord.SelectOption(label="作業ログを表示", value="worklog", emoji="📜", description="自分の直近の作業ログを表示"),
            discord.SelectOption(label="機材を登録", value="gear_add", emoji="🎛️", description="使用機材/プラグインを登録"),
            discord.SelectOption(label="機材を検索", value="gear_search", emoji="🔍", description="カテゴリ/製品名で機材を検索"),
            discord.SelectOption(label="自分の機材一覧", value="gear_list", emoji="🗂️", description="自分の登録機材一覧を表示"),
            discord.SelectOption(label="ミックスチェック依頼", value="mixcheck_submit", emoji="🎚️", description="音源URLを添えてレビュー依頼"),
            discord.SelectOption(label="ミックスチェック待ち一覧", value="mixcheck_queue", emoji="⏳", description="レビュー待ちの一覧を表示"),
        ]
        super().__init__(
            placeholder="📋 情報共有・進行管理",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dtm_panel:progress",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await _dispatch(interaction.client, interaction, self.values[0])


class AnnounceSelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(label="リリース告知", value="announce_release", emoji="🎵", description="新曲・新作のリリース告知を投稿"),
            discord.SelectOption(label="コラボ募集告知", value="announce_collab", emoji="🤝", description="コラボ募集の告知を投稿"),
            discord.SelectOption(label="セッション日程調整", value="session_propose", emoji="🗓️", description="練習/セッションの日程をリアクション投票で提案"),
        ]
        super().__init__(
            placeholder="📣 告知・日程調整",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dtm_panel:announce",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await _dispatch(interaction.client, interaction, self.values[0])


class DTMPanelView(discord.ui.View):
    """固定custom_idを使うグローバル永続View。再起動後も機能する"""

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(BasicSelect())
        self.add_item(TheorySelect())
        self.add_item(ProgressSelect())
        self.add_item(AnnounceSelect())


# ─────────────────────────────────────────────
#  Cog 本体
# ─────────────────────────────────────────────

class Panel(commands.Cog):
    """全機能をリストボックスから操作できる常設パネル"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.add_view(DTMPanelView())

    @app_commands.command(
        name="setup_panel",
        description="全機能をリストボックスから操作できる操作パネルをこのチャンネルに設置します(管理者用)",
    )
    @app_commands.describe(channel="操作パネルを設置するチャンネル(スレッドも指定可)")
    @app_commands.default_permissions(manage_guild=True)
    async def setup_panel(
        self, interaction: discord.Interaction, channel: discord.TextChannel | discord.Thread
    ) -> None:
        embed = discord.Embed(
            title="🎛️ 操作パネル",
            description=(
                "下のリストボックスからコマンドを選んで操作できます。\n"
                "・🔧 基本コマンド\n"
                "・🎵 音楽制作補助(BPM/スケール/コード進行/メトロノーム)\n"
                "・📋 情報共有・進行管理(プロジェクト/作業ログ/機材/ミックスチェック)\n"
                "・📣 告知・日程調整\n\n"
                "詳細な引数(他メンバー指定・ロール通知など)を使いたい場合は、"
                "引き続き `/` コマンドも利用できます。"
            ),
            color=discord.Color.blurple(),
        )

        try:
            await channel.send(embed=embed, view=DTMPanelView())
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ {channel.mention} にメッセージを送信する権限がありません。", ephemeral=True
            )
            return

        await interaction.response.send_message(f"✅ 操作パネルを {channel.mention} に設置しました。", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Panel(bot))
