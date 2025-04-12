import os

import discord
from dotenv import load_dotenv
from utils.ai import chat

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        msgs = []

        #如果有回覆
        if message.reference:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            if replied_message.author != bot.user:
                author = F"{replied_message.author.global_name}"
                cotent = F"{replied_message.content}"
                msgs.append({
                    "role": "user",
                    "content": F"{author}:{cotent}"
                })

        author = F"{message.author.global_name}"
        cotent = message.content.replace(F"<@{bot.user.id}>", "")

        msgs.append({
            "role": "user",
            "content": F"{author}:{cotent}"
        })

        async with message.channel.typing():
            async for resp in chat(msgs):
                if resp['status'] != 'success':
                    await message.channel.send(resp['response'])
                    return

                if "used_calls" in resp.keys():
                    calls = ""
                    for call in resp['used_calls']:
                        calls += F"`{call}` "
                    await message.channel.send(F"> {calls}\n{resp['response']}")
                else:
                    await message.channel.send(resp['response'])

if __name__ == '__main__':
    extensions = [
        'cogs.ping',
        'cogs.reader',
        'cogs.msg',

    ]
    for extension in extensions:
        bot.load_extension(extension)

load_dotenv()
bot.run(os.getenv('TOKEN'))
