# DTMServer_info_bot

DTM(音楽制作)サーバー向けの多機能Discord Bot。機能はCog単位で `cogs/` に追加していく構成。

## セットアップ

1. Python 3.10+ を用意する
2. 依存関係をインストール

   ```
   pip install -r requirements.txt
   ```

3. `.env.example` を `.env` にコピーし、[Discord Developer Portal](https://discord.com/developers/applications) で発行したBotトークンを設定する

   ```
   DISCORD_TOKEN=xxxxx
   GUILD_ID=          # 開発中は自分のサーバーIDを入れるとコマンド反映が速い
   ```

4. Botに以下のIntentsを有効化しておく(Developer Portal > Bot > Privileged Gateway Intents)
   - MESSAGE CONTENT INTENT

5. メトロノーム機能を使う場合は `ffmpeg` をインストールしてPATHを通しておく
   - Windows: [gyan.dev のビルド](https://www.gyan.dev/ffmpeg/builds/) からダウンロードして展開しPATHに追加
   - Docker利用時はDockerfileに同梱済みなので不要

6. Botを起動

   ```
   python bot.py
   ```

データ(作業ログ・機材DBなど)は起動時に自動生成される `data/bot.db` (SQLite) に保存される。

## 実装済みコマンド

### 基本

- `/ping` - 疎通確認
- `/serverinfo` - サーバー情報(メンバー数、ロール数など)を表示

### 音楽制作補助

- `/bpmdelay <bpm>` - BPMからディレイ/LFOに使えるms換算表を表示
- `/scale <root> <scale>` - 指定したキー・スケールの構成音を表示
- `/chords <root> <mode>` - 指定したキーの定番コード進行(王道進行、カノン進行、小室進行など)を一覧表示
- `/chordrandom <root> <mode>` - 定番コード進行からランダムに1つ提案
- `/metronome_start <bpm>` - 実行者のいるボイスチャンネルでクリック音を再生
- `/metronome_stop` - メトロノームを停止して退出

### 情報共有・進行管理

- `/projects [count]` - チャンネルに投稿されたDAWプロジェクトファイル(.flp/.als/.zipなど)を自動記録し一覧表示(添付時は📁を自動リアクション)
- `/log <content>` - 今日の作業ログを記録
- `/worklog [member] [count]` - 作業ログを表示
- `/gear_add <category> <name>` - 使用機材/プラグインを登録
- `/gear_search <keyword>` - 機材をカテゴリ/製品名で検索
- `/gear_list [member]` - メンバーの登録機材一覧を表示
- `/mixcheck_submit <url> [note]` - ミックスチェックを依頼(✅リアクションでレビュー完了にできる)
- `/mixcheck_queue` - レビュー待ちの一覧を表示
- `/announce_release <title> <url> [note] [image_url] [mention_role]` - リリース告知テンプレを投稿
- `/announce_collab <title> <description> [deadline] [mention_role]` - コラボ募集告知テンプレを投稿
- `/session_propose <date> [note]` - 練習/セッションの日程調整をリアクション投票で実施

## 機能追加の仕方

`cogs/` 配下に新しい `.py` ファイルを追加し、`commands.Cog` を継承したクラスと `setup(bot)` 関数を定義すれば、起動時に自動で読み込まれる。

```python
from discord.ext import commands

class MyFeature(commands.Cog):
    ...

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyFeature(bot))
```

## デプロイ

### Railway

1. Railwayダッシュボードで「New Project」→「Deploy from GitHub repo」からこのリポジトリを選択する
2. `railway.json` によりDockerfileビルドが自動選択される
3. Variables に `DISCORD_TOKEN` を設定する(`GUILD_ID` は任意)
4. このBotはWebサーバーではない常駐ワーカーなので、Settings で公開ポートの割り当ては不要
5. `data/bot.db` (作業ログ・機材DBなど) を再デプロイ後も残したい場合は、Settings → Volumes で `/app/data` にVolumeをマウントする(マウントしないと再デプロイのたびにDBが初期化される)

### 汎用 VPS / Docker

```
docker build -t dtm-bot .
docker run -d --env-file .env -v $(pwd)/data:/app/data --name dtm-bot dtm-bot
```
