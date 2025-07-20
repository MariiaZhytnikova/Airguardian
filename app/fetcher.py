import os
import httpx
import requests
from dotenv import load_dotenv

load_dotenv()  # Make sure to load .env variables

DRONES_API = os.getenv("DRONES_API")
DRONES_LIST_API = os.getenv("DRONES_LIST_API")

def fetch_owner(owner_id: str):
	base_url = os.getenv("DRONES_API")
	url = f"{base_url}{owner_id}"

	response = requests.get(url) 

	if response.status_code == 200:
		return response.json()
	return None

async def fetch_drones():
	async with httpx.AsyncClient() as client:
		response = await client.get(DRONES_LIST_API)
		response.raise_for_status()
		return response.json()