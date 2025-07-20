from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import httpx
import os
import io
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles

########### OWN ##########################
from app.fetcher import fetch_drones, fetch_owner
from app.drone_db import SessionLocal, engine
from app.schemas import ViolationOut, ViolationInput, OwnerOut
from app.model import Owner, Violation, Base
from app.utils import get_db
from app.tasks import scan_for_violations
from app.logger import logger
from app.error_handlers import (
	validation_exception_handler,
	http_exception_handler,
	unhandled_exception_handler
)
####################################

load_dotenv()
X_SECRET = os.getenv("X_SECRET")
DRONES_LIST_API = os.getenv("DRONES_LIST_API")

app = FastAPI()
#app.mount("/", StaticFiles(directory="static", html=True), name="static")

######################################################
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
######################################################

#Allows frontend js to communicate with FASTAPI backend
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:8080"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
######################################################

@app.on_event("startup")
def on_startup():
	Base.metadata.create_all(bind=engine)
	print("  🗃️       Tables created.")

@app.get("/health")
def health_check():
	return {"success": "ok"}

# @app.get("/drones")
# async def proxy_drones():
# 	try:
# 		drones = await fetch_drones()
# 	except httpx.RequestError as exc:
# 		raise HTTPException(status_code=502, detail=f"Error contacting drones API: {exc}")
# 	except httpx.HTTPStatusError as exc:
# 		raise HTTPException(status_code=exc.response.status_code, detail=f"Drones API error: {exc.response.text}")

# 	return drones
logger.info("App starting...")
@app.get("/drones")
async def proxy_drones(limit: int = Query(10, gt=0, le=100)):
	try:
		drones = await fetch_drones()
	except httpx.RequestError as exc:
		raise HTTPException(status_code=502, detail=f"Error contacting drones API: {exc}")
	except httpx.HTTPStatusError as exc:
		raise HTTPException(status_code=exc.response.status_code, detail=f"Drones API error: {exc.response.text}")

	logger.info(f"Returning first {limit} drones")
	return drones[:limit]

# GET /nfz: Returns violations from the last 24 hours
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


# Use a proxy/backend to attach the secret
@app.get("/frontend-nfz")
def frontend_proxy_nfz(db: Session = Depends(get_db)):
	# This does NOT expose the secret to the client
	if X_SECRET is None:
		raise HTTPException(status_code=500, detail="Missing secret key")

	# Internally call the protected route
	scan_for_violations.delay()
	since = datetime.utcnow() - timedelta(hours=24)
	violations = (
		db.query(Violation)
		.filter(Violation.timestamp >= since)
		.options(joinedload(Violation.owner))
		.all()
	)
	return [ViolationOut.from_orm(v) for v in violations]

@app.get("/map")
async def map_image():

	# Try fetching drones only once
	try:
		drones = await fetch_drones()
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"Failed to fetch drones: {str(e)}")

	NFZ_RADIUS = 1000

	fig, ax = plt.subplots(figsize=(8, 8))

	# Draw smaller no-fly zone circle at center
	no_fly_zone = patches.Circle(
		(0, 0),
		radius=NFZ_RADIUS,
		edgecolor='blue',
		facecolor='lightblue',
		alpha=0.3,
		label='No-Fly Zone (radius=100)'
	)
	ax.add_patch(no_fly_zone)

	# Plot drones (red if inside NFZ, green if outside)
	for drone in drones:
		try:
			x = drone["x"]
			y = drone["y"]
		except KeyError:
			continue

		dist = (x**2 + y**2) ** 0.5
		color = "red" if dist <= NFZ_RADIUS else "green"
		ax.scatter(x, y, c=color)

		if dist <= NFZ_RADIUS:
			try:
				owner_id = drone["owner_id"]
			except Exception:
				owner_id = "unknown"

			# Add label slightly above the drone
			ax.text(x, y + 100, owner_id, fontsize=8, color='black', ha='center')

	ax.set_xlim(-4000, 4000)
	ax.set_ylim(-4000, 4000)
	ax.set_aspect('equal', 'box')
	ax.set_title("Live Drones & No-Fly Zone")
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.legend()

	buf = io.BytesIO()
	plt.savefig(buf, format="png")
	plt.close(fig)
	buf.seek(0)

	return StreamingResponse(buf, media_type="image/png")

@app.get("/api/map-data")
async def get_map_data():
	try:
		drones = await fetch_drones()
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"Failed to fetch drones: {str(e)}")
	
	return {"drones": drones, "nfz_radius": 1000}
