# 🎵 Discord Music Bot

Python (`discord.py`) と **Wavelink (Lavalink)** を使用した、高機能かつ軽量なDiscord音楽Botです。
YouTubeからの再生、プレイリスト対応、DJロールによる権限管理機能を備えています。

## ✨ 主な機能 (Features)

* **再生 (`/play`)**: URLまたはキーワード検索で音楽を再生（オートコンプリート対応）。
* **キュー管理**: 再生待ちリストの表示、ページネーション、シャッフル機能。
* **ループ再生**: 1曲ループ / 全曲ループ / オフ の切り替え。
* **権限管理**: スキップ、停止、シャッフル等の操作は「**DJ**」ロールまたは管理者権限が必要。
* **リッチな通知**: 曲の開始時に埋め込みメッセージ（Embed）で通知。
* **Docker対応**: Docker Composeを使用した一発起動に対応。

今のところ、YouTubeのみに対応しています。

## 📦 動作要件 (Prerequisites)

このBotは **Ubuntu 24.04 LTS** での動作を推奨しています。

* **OS**: Linux (Ubuntu 24.04 LTS 推奨)
* **Python**: 3.10 以上
* **Java**: 17 以上 (Lavalinkサーバーの実行に必要)
* **Lavalink**: v4 以上

## 🚀 インストール & セットアップ (Installation)

### 1. システムパッケージの更新 (Ubuntu 24.04)
必要なパッケージ（Git, Python, Java等）をインストールします。

```bash
sudo apt update
sudo apt install -y git python3-pip python3-venv openjdk-17-jre-headless
```

### 2. リポジトリのクローン

```bash
git clone https://github.com/ch4rindo/Ongakun-MusicBot
cd Ongakun-MusicBot
```

### 3. 仮想環境の作成と依存ライブラリのインストール

システム環境への影響を防ぐため、仮想環境 (`venv`) の使用を強く推奨します。

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# ライブラリのインストール
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
cp .env.example .env
nano .env
```

**.env の内容:**

```env
# Discord Developer Portalから取得したToken
DISCORD_TOKEN=your_discord_bot_token_here

# Lavalinkサーバー設定 (デフォルト値)
LAVALINK_URI=[http://127.0.0.1:2333](http://127.0.0.1:2333)
LAVALINK_PASS=youshallnotpass
```

### 5. Lavalinkサーバーの準備

Botが音声を再生するにはバックエンドとしてLavalinkが必要です。

1. [Lavalink GitHub Releases](https://github.com/lavalink-devs/Lavalink/releases) から最新の `Lavalink.jar` (v4推奨) をダウンロードします。
2. 同ディレクトリに `application.yml` を配置します（[サンプル設定](https://github.com/lavalink-devs/Lavalink/blob/master/LavalinkServer/application.yml.example)を参照）。
3. サーバーを起動します。

```bash
# バックグラウンドで実行するか、別の端末で実行してください
java -jar Lavalink.jar
```

## 🎮 実行方法 (Usage)

Lavalinkが起動している状態で、Botを起動します。

```bash
# 仮想環境を有効化 (まだの場合)
source venv/bin/activate

# Botの起動
python main.py
```

## 📝 コマンド一覧 (Commands)

すべての機能はスラッシュコマンド (`/`) として提供されます。

| コマンド | 引数 | 説明 | 必要な権限 |
| --- | --- | --- | --- |
| `/play` | `search` | 曲名/URLで検索して再生 (サジェスト付) | 誰でも |
| `/queue` | なし | 現在の再生待ちリストを表示 | 誰でも |
| `/nowplaying` | なし | 再生中の曲情報を表示 | 誰でも |
| `/skip` | なし | 現在の曲をスキップ | **DJ / Admin** |
| `/stop` | なし | 再生を停止し、Botを切断 | **DJ / Admin** |
| `/shuffle` | なし | キューの中身をシャッフル | **DJ / Admin** |
| `/loop` | なし | ループ切替 (オフ → 1曲 → 全曲) | **DJ / Admin** |

### 権限について (DJ Role)

`skip` や `stop` などの操作コマンドを実行するには、Discordサーバー側で以下のいずれかの条件を満たす必要があります：

1. **"DJ"** という名前のロールを持っている。
2. サーバーの **管理者権限 (Administrator)** を持っている。

## 🐳 Dockerでの実行 (Optional)

ここまでだらだら説明しましたが、Docker使うと簡単にセットアップできます。
プロジェクトルートに `compose.yml` が用意されています。以下の手順で起動してください。

```bash
docker compose up -d --build
```
これにより、LavalinkサーバーとMusic Botが連携した状態で起動します。

## ⚠️ 免責事項
このBotは教育および個人的な使用を目的としています。YouTube等の利用規約を遵守してご利用ください。
