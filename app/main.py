from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List
from app.config import settings

import httpx
import os

# --------------------OWN--------------------------------
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
# ---------------------------------------------------------

app = FastAPI()

# ---------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
# ---------------------------------------------------------

# ---------------------------------------------------------
# CORS (backend <-> frontend)
# ---------------------------------------------------------
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:8080"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# ---------------------------------------------------------
# Startup: ensure tables exist
# ---------------------------------------------------------

@app.on_event("startup")
def on_startup():
	Base.metadata.create_all(bind=engine)
	print("  🗃️       Tables created.")


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
	return {"success": "ok"}

logger.info("App starting...")

# ---------------------------------------------------------
# Drones proxy
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Secure NFZ violations endpoint
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Frontend-safe NFZ: does NOT expose secret to browser
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Map data
# ---------------------------------------------------------
@app.get("/api/map-data")
async def get_map_data():
	try:
		drones = await fetch_drones()
	except Exception as e:
		raise HTTPException(status_code=502, detail=f"Failed to fetch drones: {str(e)}")
	
	return {"drones": drones, "nfz_radius": 1000}
