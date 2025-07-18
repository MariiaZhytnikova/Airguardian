import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Make sure to load .env variables

def fetch_owner(owner_id: str):
	base_url = os.getenv("DRONES_API")
	url = f"{base_url}{owner_id}"

	if response.status_code == 200:
		return response.json()
	return None
