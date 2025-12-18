import discord
from discord.ext import commands
import wavelink
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LAVALINK_URI = os.getenv('LAVALINK_URI', 'http://127.0.0.1:2333')
LAVALINK_PASS = os.getenv('LAVALINK_PASS', 'youshallnotpass')


class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        node = wavelink.Node(
            uri=LAVALINK_URI,
            password=LAVALINK_PASS,
        )
        await wavelink.Pool.connect(client=self, nodes=[node], cache_capacity=100)

        try:
            await self.load_extension('cogs.music')
            print("Extension 'cogs.music' loaded.")
        except Exception as e:
            print(f"Failed to load extension: {e}")

        try:
            await self.tree.sync()
            print("コマンド同期完了")
        except Exception as e:
            print(f"コマンド同期エラー: {e}")

    async def on_ready(self):
        print(f'{self.user} としてログインしました！')


if __name__ == "__main__":
    bot = MusicBot()
    bot.run(DISCORD_TOKEN)