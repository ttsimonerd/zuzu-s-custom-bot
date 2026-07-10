import aiohttp
import os

N8N_RANDOM_WEBHOOK = os.getenv("N8N_RANDOM_WEBHOOK")

async def trigger_random(payload):

    async with aiohttp.ClientSession() as session:

        async with session.post(
            N8N_RANDOM_WEBHOOK,
            json=payload
        ) as response:

            return await response.json()
