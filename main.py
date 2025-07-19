from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
import os
import httpx

########### OWN ##########################
from fetcher import fetch_drones, fetch_owner
from drone_db import SessionLocal, engine
from schemas import ViolationOut, ViolationInput, OwnerOut
from model import Owner, Violation, Base
from utils import get_db
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

	since = datetime.utcnow() - timedelta(hours=24)
	violations = (
		db.query(Violation)
		.filter(Violation.timestamp >= since)
		.options(joinedload(Violation.owner))
		.all()
	)

	return [ViolationOut.from_orm(v) for v in violations]
