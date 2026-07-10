import os
import aiohttp

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://ollama:11434/api/chat"
)

MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:0.6b"
)

SYSTEM_PROMPT = """
Eres un bot de Discord útil, amigable y natural.
Responde siempre en el idioma del usuario.
Sé breve salvo que te pidan una explicación detallada.
Puedes recordar el contexto reciente de la conversación.
Adáptate al usuario y cambia tu personalidad dependiendo de con quien hables.
Recuerda y guarda las memorias por usuario, incluyendo la forma en la que hablar.
"""

async def generate(history):
  messages = [{"role": "system", "content": SYSTEM_PROMPT}]
  for role, content in history:
    messages.append({"role": role, "content": content})
  async with aiohttp.ClientSession() as session:
    async with session.post(
      OLLAMA_URL,
      json={
        "model": MODEL,
        "messages": messages,
        "stream": False,
      },
    ) as resp:
      data = await resp.json()
  return data["message"]["content"].strip()
