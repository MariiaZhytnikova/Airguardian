from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import httpx
import os
import io

########### OWN ##########################
from fetcher import fetch_drones, fetch_owner
from drone_db import SessionLocal, engine
from schemas import ViolationOut, ViolationInput, OwnerOut
from model import Owner, Violation, Base
from utils import get_db
from tasks import scan_for_violations
####################################

load_dotenv()
X_SECRET = os.getenv("X_SECRET")
DRONES_LIST_API = os.getenv("DRONES_LIST_API")

app = FastAPI()

@app.on_event("startup")
def on_startup():
	Base.metadata.create_all(bind=engine)
	print("🗃️ Tables created.")

@app.get("/health")
def health_check():
	return {"success": "ok"}

@app.get("/drones")
async def proxy_drones():
	try:
		drones = await fetch_drones()
	except httpx.RequestError as exc:
		raise HTTPException(status_code=502, detail=f"Error contacting drones API: {exc}")
	except httpx.HTTPStatusError as exc:
		raise HTTPException(status_code=exc.response.status_code, detail=f"Drones API error: {exc.response.text}")

	return drones

@app.get("/nfz")
def get_violations(
	x_secret: str = Header(...),
	db: Session = Depends(get_db)
):
	if x_secret != X_SECRET:
		raise HTTPException(status_code=401, detail="Unauthorized")

 # 🔁 Trigger background scan before returning results
	scan_for_violations.delay()

	since = datetime.utcnow() - timedelta(hours=24)
	violations = (
		db.query(Violation)
		.filter(Violation.timestamp >= since)
		.options(joinedload(Violation.owner))
		.all()
	)

	return [ViolationOut.from_orm(v) for v in violations]

# # • GET /nfz: Returns violations from the last 24 hours
@app.get("/map")
async def map_image(
	x_secret: str = Header(...),
):
	if x_secret != X_SECRET:
		raise HTTPException(status_code=401, detail="Unauthorized")

	# Get real-time drones
	try:
		drones = await fetch_drones()
	except httpx.RequestError as exc:
		raise HTTPException(status_code=502, detail=f"Error contacting drones API: {exc}")
	except httpx.HTTPStatusError as exc:
		raise HTTPException(status_code=exc.response.status_code, detail=f"Drones API error: {exc.response.text}")

	# NFZ radius (assumption: 100 meters, origin at (0,0))
	NFZ_RADIUS = 100.0

	fig, ax = plt.subplots(figsize=(6, 6))

	# Draw the no-fly zone circle
	no_fly_zone = patches.Circle((0, 0), radius=1000, edgecolor='blue', facecolor='lightblue', alpha=0.3, label='No-Fly Zone')
	ax.add_patch(no_fly_zone)

	ax.set_xlim(-1100, 1100)
	ax.set_ylim(-1100, 1100)
	ax.set_aspect('equal', 'box')  # keep circle shape
	ax.legend()
	plt.show()

	try:
		drones = await fetch_drones()
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"Failed to fetch drones: {str(e)}")

	NFZ_RADIUS = 100.0  # або інше значення

	for drone in drones:
		try:
			x = drone["x"]
			y = drone["y"]
		except KeyError:
			continue  # пропустити дронів без координат

		dist = (x**2 + y**2) ** 0.5
		color = "red" if dist < NFZ_RADIUS else "green"
		ax.scatter(x, y, c=color)

	ax.set_xlim(-1100, 1100)
	ax.set_ylim(-1100, 1100)
	ax.set_title("Live Drones & NFZ")
	ax.set_xlabel("X")
	ax.set_ylabel("Y")

	buf = io.BytesIO()
	plt.savefig(buf, format="png")
	plt.close(fig)
	buf.seek(0)

	return StreamingResponse(buf, media_type="image/png")
