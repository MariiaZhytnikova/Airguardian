from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import matplotlib
matplotlib.use("Agg")
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

from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from error_handlers import (
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler
)
from logger import logger  # You can now use logger.info(), logger.error(), etc.
#from fastapi import HTTPException
###############################################

load_dotenv()
X_SECRET = os.getenv("X_SECRET")
DRONES_LIST_API = os.getenv("DRONES_LIST_API")

app = FastAPI()

#################################################
#Allows frontend js to communicate with FASTAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#################################################
# Register custom error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
#####################################################
# Example route to test logger
@app.get("/test")
def test():
    logger.info("Test endpoint called")
    return {"message": "Hello from Airguardian"}
#######################################################
@app.on_event("startup")
def on_startup():
	Base.metadata.create_all(bind=engine)
	print("  🗃️       Tables created.")

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

# # • GET /nfz: Returns violations from the last 24 hours
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
				owner = await fetch_owner(serial)
				owner_id = owner.get("pilotId", "unknown")
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

@app.get("/nfz-dev")  # A temporary endpoint without header requirement
def get_violations_dev(
	db: Session = Depends(get_db)
):
	since = datetime.utcnow() - timedelta(hours=24)
	violations = (
		db.query(Violation)
		.filter(Violation.timestamp >= since)
		.options(joinedload(Violation.owner))
		.all()
	)
	return [ViolationOut.from_orm(v) for v in violations]