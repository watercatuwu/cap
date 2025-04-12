
from discord import (ApplicationContext, Embed, IntegrationType,
                     InteractionContextType, Member, Option)
from discord.ext import commands

class msg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='delete',
        description='delete msgs',
        integration_types=[
            IntegrationType.user_install,
            IntegrationType.guild_install,
        ],
        contexts=[
            InteractionContextType.guild,
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
        ],
    )
    async def delete(
        self,
        ctx: ApplicationContext,
        member: Option(Member, "member", required=True),
        qty: Option(int, "qty", required=True, default=1),
    ):
        channel = ctx.channel
        massages = await channel.history(limit=qty).flatten()
        for message in massages:
            if message.author == member:
                await message.delete()
        await ctx.respond(F"Successfully deleted {qty} messages", ephemeral=True)


    @commands.slash_command(
        name='talk',
        description='talk with ai',
        integration_types=[
            IntegrationType.user_install,
            IntegrationType.guild_install,
        ],
        contexts=[
            InteractionContextType.guild,
            InteractionContextType.bot_dm,
            InteractionContextType.private_channel,
        ],
    )
    async def talk(
        self,
        ctx: ApplicationContext,
        content: Option(str, "content", required=True)
    ):
        channel = ctx.channel
        massages = await channel.history(limit=qty).flatten()
        for message in massages:
            if message.author == member:
                await message.delete()
        await ctx.respond(F"Successfully deleted {qty} messages", ephemeral=True)


def setup(bot):
    bot.add_cog(msg(bot))
