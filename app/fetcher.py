import httpx
import requests

from app.config import settings


# Read API URLs from config
DRONES_API = settings.DRONES_API
DRONES_LIST_API = settings.DRONES_LIST_API


def fetch_owner(owner_id: str):
    url = f"{DRONES_API}{owner_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None


async def fetch_drones():
    async with httpx.AsyncClient() as client:
        response = await client.get(DRONES_LIST_API)
        response.raise_for_status()
        return response.json()
