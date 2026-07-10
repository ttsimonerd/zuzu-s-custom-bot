import os
import discord
import aiosqlite
from discord import app_commands
from dotenv import load_dotenv

from ai import generate
from memory import init_db, add_message, get_recent

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
AI_PASSWORD = os.getenv("AI_PASSWORD")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

DB = "data/memory.db"

intents = discord.Intents.default()
intents.message_content = True


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await init_db()
        await init_settings()
        await self.tree.sync()

client = MyClient()


async def init_settings():
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        await db.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES('ai_enabled', 'true')"
        )

        await db.commit()

async def get_ai_enabled():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key='ai_enabled'"
        )
        row = await cursor.fetchone()

    return row is None or row[0].lower() == "true"

async def set_ai_enabled(value: bool):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "REPLACE INTO settings(key, value) VALUES('ai_enabled', ?)",
            ("true" if value else "false",)
        )
        await db.commit()


@client.event
async def on_ready():
    print(f"Conectado como {client.user}")


@client.tree.command(name="ai", description="AI Stats (Dev Only) ")
@app_commands.describe(
    action="on, off o status",
    password="Pass Required"
)
async def ai_command(
    interaction: discord.Interaction,
    action: str,
    password: str | None = None
):
    action = action.lower()

    if action not in ("on", "off", "status"):
        await interaction.response.send_message(
            "B-Baka! Usa `on`, `off` o `status`... (＞﹏＜)",
            ephemeral=True
        )
        return

    if action == "status":
        enabled = await get_ai_enabled()

        msg = (
            "L-La IA está activada... N-No es que me alegre hablar contigo ni nada... ♡"
            if enabled else
            "*pouts* La IA está desactivada ahora mismo..."
        )

        await interaction.response.send_message(
            msg,
            ephemeral=True
        )
        return

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "N-No tienes permiso para hacer eso! (╥﹏╥)",
            ephemeral=True
        )
        return

    if password != AI_PASSWORD:
        await interaction.response.send_message(
            "L-La contraseña es incorrecta...! (＞﹏＜)",
            ephemeral=True
        )
        return

    enabled = action == "on"

    await set_ai_enabled(enabled)

    if enabled:
        msg = (
            "Hmph! La IA ha sido activada... "
            "Puedes hablarme otra vez, supongo~ ♡"
        )
    else:
        msg = (
            "*crosses arms* La IA ha sido desactivada... "
            "N-No es que quisiera hablar con vosotros de todas formas... ♡"
        )

    await interaction.response.send_message(
        msg,
        ephemeral=True
    )

@client.tree.command(
    name="info",
    description="The Creator"
)
async def info(interaction: discord.Interaction):

    prompt = """
Presenta a tu creador con tu personalidad tsundere y kawaii.

Información:
- Nombre: ttsmcz
- Intereses: python, self-hosting.
- Crea proyectos y busca crecer en apps como Github (github.com/ttsimonerd).
- Es el creador y administrador principal de este bot.
- Esta empezando en el mundo del hosting con un servidor custom que ha montado, en el cual esta alojado este bot y esta IA.

Habla como una tsundere adorable usando algunos kaomojis y acciones entre asteriscos.
No inventes información que no aparezca aquí.
"""

    async with interaction.channel.typing():
        response = await generate([
            ("user", prompt)
        ])

    if len(response) > 1900:
        response = response[:1900] + "..."

    await interaction.response.send_message(response)


@client.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    if not await get_ai_enabled():
        return

    if client.user not in message.mentions:
        return

    content = message.content

    for mention in [
        f"<@{client.user.id}>",
        f"<@!{client.user.id}>"
    ]:
        content = content.replace(
            mention,
            ""
        )

    content = content.strip()

    if not content:
        content = (
            "El usuario te ha mencionado sin escribir nada. "
            "Salúdalo brevemente con personalidad tsundere y kawaii."
        )

    await add_message(
        str(message.author.id),
        str(message.channel.id),
        "user",
        content,
    )

    async with message.channel.typing():

        history = await get_recent(
            str(message.channel.id)
        )

        response = await generate(
            history
        )

    await add_message(
        str(message.author.id),
        str(message.channel.id),
        "assistant",
        response,
    )

    if len(response) > 1900:
        response = response[:1900] + "..."

    await message.reply(response)

client.run(TOKEN)
