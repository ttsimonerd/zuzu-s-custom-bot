import os
import discord
from dotenv import load_dotenv

from ai import generate
from memory import init_db, add_message, get_recent

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await init_db()
    print(f"Conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Br el handle de las mentions
    if client.user not in message.mentions:
        return

    content = message.content

    for mention in [f"<@{client.user.id}>", f"<@!{client.user.id}>"]:
        content = content.replace(mention, "")

    content = content.strip()

    if not content:
        await message.reply("Hola! Si necesitas algo, incluye un mensaje a parte de mi tag...")
        return

    await add_message(
        str(message.author.id),
        str(message.channel.id),
        "user",
        content,
    )

    async with message.channel.typing():
        history = await get_recent(str(message.channel.id))
        response = await generate(history)
# Aqui pa que se guarden los mensajes en la db
    await add_message(
        str(message.author.id),
        str(message.channel.id),
        "assistant",
        response,
    )
# Limite de chs de discord :(
    if len(response) > 1900:
        response = response[:1900] + "..."

    await message.reply(response)
# Me tengo que acordar de poner el token
client.run(TOKEN)
