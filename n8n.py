import aiohttp
import asyncio
import json
import os

N8N_RANDOM_WEBHOOK = os.getenv("N8N_RANDOM_WEBHOOK")

async def trigger_random(payload):
    if not N8N_RANDOM_WEBHOOK:
        return {
            "success": False,
            "error": "N8N_RANDOM_WEBHOOK no está configurado."
        }

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(
                N8N_RANDOM_WEBHOOK,
                json=payload
            ) as response:
                text = await response.text()
                if response.status >= 400:
                    return {
                        "success": False,
                        "error": (
                            f"Webhook de n8n devolvió estado {response.status}: "
                            f"{text[:200]}"
                        )
                    }
                try:
                    data = json.loads(text)
                except ValueError:
                    return {
                        "success": True,
                        "message": text or "Respuesta inválida de n8n."
                    }
        except aiohttp.ClientError as exc:
            return {
                "success": False,
                "error": f"Error de conexión a n8n: {exc}"
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Tiempo de espera agotado al contactar con n8n."
            }

    if not isinstance(data, dict):
        return {
            "success": True,
            "message": str(data)
        }

    return {
        "success": data.get("success", True),
        "message": data.get("message") or data.get("result") or str(data),
        "error": data.get("error")
    }
