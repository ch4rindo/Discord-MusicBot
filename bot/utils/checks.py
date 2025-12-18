import discord
from discord import app_commands


def is_dj_or_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True

        role_names = [role.name.lower() for role in interaction.user.roles]
        if "dj" in role_names:
            return True

        await interaction.response.send_message(
            "❌ このコマンドを実行するには **'DJ'** ロールか管理者権限が必要です。",
            ephemeral=True
        )
        return False

    return app_commands.check(predicate)