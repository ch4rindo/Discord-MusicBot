import discord
from discord.ui import View, Button
import wavelink
import math


class QueuePaginator(View):
    def __init__(self, interaction: discord.Interaction, player: wavelink.Player, items_per_page: int = 10):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.player = player
        self.queue = player.queue
        self.items_per_page = items_per_page
        self.current_page = 0
        self.max_page = max(0, math.ceil(len(self.queue) / self.items_per_page) - 1)
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == self.max_page) or (len(self.queue) == 0)

    def get_embed(self):
        embed = discord.Embed(title="🎵 再生待ちリスト (Queue)", color=discord.Color.blurple())

        mode_text = "オフ"
        if self.player.queue.mode == wavelink.QueueMode.loop:
            mode_text = "🔂 1曲ループ"
        elif self.player.queue.mode == wavelink.QueueMode.loop_all:
            mode_text = "🔁 全曲ループ"

        embed.set_author(name=f"ループ設定: {mode_text}")

        if not self.queue:
            embed.description = "キューは空です。"
            return embed

        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = list(self.queue)[start:end]

        description = ""
        for i, track in enumerate(page_items, start=start + 1):
            description += f"**{i}.** [{track.title}]({track.uri}) - `{int(track.length // 1000 // 60)}:{int(track.length // 1000 % 60):02d}`\n"

        embed.description = description
        embed.set_footer(text=f"ページ {self.current_page + 1} / {self.max_page + 1} | 合計: {len(self.queue)}曲")
        return embed

    @discord.ui.button(label="◀ 前へ", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="次へ ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            pass
        except:
            pass