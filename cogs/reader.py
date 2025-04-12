
from discord import (ApplicationContext, Embed, IntegrationType,
                     InteractionContextType, ui, Option)
from discord.ext import commands
from utils.ai import chat_api

class reader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='read',
        description='read msgs',
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
    async def read(
        self,
        ctx: ApplicationContext,
        after: Option(str, "after msgid", required=True),
        before: Option(str, "before msgid", required=False, default=None),
        prompts: Option(str, "prompts", required=False, default=""),
    ):
        await ctx.respond("waiting for response...<a:Sussy:1359759061071167660>", ephemeral=True)

        channel = ctx.channel
        after = await ctx.fetch_message(after)
        if before:
            before = await ctx.fetch_message(before)

        messages = await channel.history(after=after, before=before).flatten() # flatten: into a list

        ai_msgs = [{
            "role": "system",
            "content": """
                你是一位社群分析助手，請從以下對話中提取出關鍵訊息，並用簡潔的方式歸納每個主要話題。對話中的每個人物及其言行應該簡要描述。你需要：
                1. 根據對話內容，辨識出至少一個主要話題。
                2. 每個話題需要標註出參與者的名字和簡單的描述。
                3. 不需要過多的細節，只需聚焦於關鍵事件和情緒，將不必要的細節省略。
                4. 每個話題應該包含發言者的情緒狀態或語氣（如自嘲、幽默、嘲諷等）。
                4. 在有多重話題時，分開處理並標明。
                範例：
                - TL (tl_is_here): 因為把三玖放進包包，鉛筆盒可能在公車站掉落。（**自嘲**，表達自己疏忽）
                - sad_owl (sad_owl.): 嘲諷TL三玖比鉛筆盒重要，並提到科學館暴雨小淹水，建議去壢中水樂園看瀑布。（**嘲諷**）
                - welson1030 (welson1030): 用「Yipee」表示對壢中水樂園積水情況的苦中作樂。（**幽默**）
                - 超萌喵糰子（宋雨琦我老婆）(miaotuanzi_0612): 描述天氣像颱風並要求風景區照片，戲稱積水像「黃河」。（**幽默**）
            """
            }]

        for message in messages:
            obj = {
                'role' : 'user',
                'name': F"{message.author.global_name}({message.author.name})",
                'content' : message.content
            }
            ai_msgs.append(obj)

        if prompts:
            ai_msgs.append({
                "role": "system",
                "content": prompts
            })

        response = await chat_api(ai_msgs)
        embed = Embed(
            title='AI Reader',
            description=f"Duration: {response['duration']:.2f} s",
            color=0xFFA46E
        )
        await ctx.edit(content="Done.")
        await ctx.author.send(content=response['response'], embed=embed)

def setup(bot):
    bot.add_cog(reader(bot))
