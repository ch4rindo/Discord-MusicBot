import discord
from discord import app_commands
from discord.ext import commands
import wavelink
from typing import List

from utils.checks import is_dj_or_admin
from utils.views import QueuePaginator


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def search_autocomplete(self, interaction: discord.Interaction, current: str) -> List[
        app_commands.Choice[str]]:
        if not current or current.startswith("http"):
            return []

        if not wavelink.Pool.nodes:
            return []

        try:
            tracks = await wavelink.Playable.search(current, source="ytsearch")
            if not tracks:
                return []

            choices = []
            for track in tracks[:25]:
                label = f"{track.title[:50]} - {track.author[:20]}"
                if len(track.uri) <= 100:
                    choices.append(app_commands.Choice(name=label, value=track.uri))
                elif len(track.title) <= 100:
                    choices.append(app_commands.Choice(name=label, value=track.title))
            return choices
        except Exception as e:
            print(f"サジェストエラー: {e}")
            return []

    # --- イベントリスナー: 曲開始時の通知 ---
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        player: wavelink.Player = payload.player
        if not player:
            return

        if hasattr(player, "home") and player.home:
            track = payload.track
            embed = discord.Embed(
                title="Now Playing 🎵",
                description=f"[{track.title}]({track.uri})",
                color=discord.Color.teal()
            )
            embed.add_field(name="アーティスト", value=track.author, inline=True)
            embed.add_field(name="長さ",
                            value=f"{int(track.length // 1000 // 60)}:{int(track.length // 1000 % 60):02d}",
                            inline=True)
            if track.artwork:
                embed.set_thumbnail(url=track.artwork)

            await player.home.send(embed=embed)

    @app_commands.command(name="play", description="URLまたはキーワードで再生 (プレイリスト対応)")
    @app_commands.describe(search="YouTubeのURL、プレイリストURL、または検索ワード")
    @app_commands.autocomplete(search=search_autocomplete)
    async def play(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer()

        if not interaction.user.voice:
            return await interaction.followup.send(
                embed=discord.Embed(description="❌ まずはボイスチャンネルに入ってください！", color=discord.Color.red())
            )

        if not interaction.guild.voice_client:
            try:
                player: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
                await player.set_volume(10)
            except Exception as e:
                return await interaction.followup.send(
                    embed=discord.Embed(description=f"❌ 接続エラー: {e}", color=discord.Color.red())
                )
        else:
            player: wavelink.Player = interaction.guild.voice_client

        # 通知先チャンネルを保存
        player.home = interaction.channel
        player.autoplay = wavelink.AutoPlayMode.partial

        try:
            if "https://" in search or "http://" in search:
                tracks = await wavelink.Playable.search(search)
            else:
                tracks = await wavelink.Playable.search(search, source="ytsearch")
        except Exception as e:
            return await interaction.followup.send(
                embed=discord.Embed(description=f"❌ 検索/読み込みエラー: {e}", color=discord.Color.red())
            )

        if not tracks:
            return await interaction.followup.send(
                embed=discord.Embed(description="❌ 曲が見つかりませんでした。", color=discord.Color.red())
            )

        embed = discord.Embed(color=discord.Color.green())

        if isinstance(tracks, wavelink.Playlist):
            added = await player.queue.put_wait(tracks)
            embed.title = "プレイリストを読み込みました"
            embed.description = f"**{tracks.name}**\n含まれる **{added}** 曲をキューに追加しました。"
            if tracks.artwork:
                embed.set_thumbnail(url=tracks.artwork)
        else:
            track = tracks[0]
            await player.queue.put_wait(track)
            embed.title = "トラックを追加しました"
            embed.description = f"🎵 **[{track.title}]({track.uri})**"
            embed.add_field(name="長さ",
                            value=f"{int(track.length // 1000 // 60)}:{int(track.length // 1000 % 60):02d}",
                            inline=True)
            embed.add_field(name="アーティスト", value=track.author, inline=True)
            if track.artwork:
                embed.set_thumbnail(url=track.artwork)

        await interaction.followup.send(embed=embed)

        if not player.playing:
            await player.play(player.queue.get())

    # --- コマンド: Shuffle ---
    @app_commands.command(name="shuffle", description="キューをシャッフルします (DJ専用)")
    @is_dj_or_admin()
    async def shuffle(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.queue:
            return await interaction.response.send_message("キューが空です。", ephemeral=True)

        player.queue.shuffle()
        embed = discord.Embed(description="🔀 キューをシャッフルしました！", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    # --- コマンド: Loop ---
    @app_commands.command(name="loop", description="ループ設定 (DJ専用)")
    @is_dj_or_admin()
    async def loop(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("接続していません。", ephemeral=True)

        if player.queue.mode == wavelink.QueueMode.normal:
            player.queue.mode = wavelink.QueueMode.loop
            msg = "🔂 **1曲ループ** に設定しました。"
        elif player.queue.mode == wavelink.QueueMode.loop:
            player.queue.mode = wavelink.QueueMode.loop_all
            msg = "🔁 **全曲ループ** に設定しました。"
        else:
            player.queue.mode = wavelink.QueueMode.normal
            msg = "➡️ ループを **オフ** にしました。"

        embed = discord.Embed(description=msg, color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    # --- コマンド: Skip ---
    @app_commands.command(name="skip", description="曲をスキップ (DJ専用)")
    @is_dj_or_admin()
    async def skip(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.playing:
            return await interaction.response.send_message("再生中の曲がありません。", ephemeral=True)
        await player.skip()
        await interaction.response.send_message(
            embed=discord.Embed(description="⏭️ スキップしました。", color=discord.Color.gold())
        )

    # --- コマンド: Stop ---
    @app_commands.command(name="stop", description="停止・切断 (DJ専用)")
    @is_dj_or_admin()
    async def stop(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("Botは接続していません。", ephemeral=True)
        await player.disconnect()
        await interaction.response.send_message(
            embed=discord.Embed(description="⏹️ 切断しました。", color=discord.Color.greyple())
        )

    # --- コマンド: Now Playing ---
    @app_commands.command(name="nowplaying", description="現在の曲を表示")
    async def nowplaying(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.current:
            return await interaction.response.send_message("何も再生していません。", ephemeral=True)

        track = player.current
        embed = discord.Embed(title="▶️ 現在再生中", description=f"[{track.title}]({track.uri})",
                              color=discord.Color.blue())
        embed.add_field(name="アーティスト", value=track.author, inline=True)

        status = "オフ"
        if player.queue.mode == wavelink.QueueMode.loop:
            status = "🔂 1曲ループ"
        elif player.queue.mode == wavelink.QueueMode.loop_all:
            status = "🔁 全曲ループ"

        embed.set_footer(text=f"ループ設定: {status}")
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
        await interaction.response.send_message(embed=embed)

    # --- コマンド: Queue ---
    @app_commands.command(name="queue", description="再生待ちリストを表示")
    async def queue(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.queue:
            return await interaction.response.send_message("キューは空です。", ephemeral=True)
        view = QueuePaginator(interaction, player)
        await interaction.response.send_message(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))