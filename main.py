from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import os
import httpx

########### OWN ##########################
from fetcher import fetch_drones, fetch_owner
from drone_db import SessionLocal, engine
from schemas import ViolationOut, ViolationInput, OwnerOut
from model import Owner, Violation, Base
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

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


########################################################################

@app.get("/drones")
async def proxy_drones():
	try:
		drones = await fetch_drones()
	except httpx.RequestError as exc:
		raise HTTPException(status_code=502, detail=f"Error contacting drones API: {exc}")
	except httpx.HTTPStatusError as exc:
		raise HTTPException(status_code=exc.response.status_code, detail=f"Drones API error: {exc.response.text}")

	return drones
######################################################3


def is_in_no_fly_zone(x: float, y: float) -> bool:
	return x ** 2 + y ** 2 <= 1000 ** 2

@app.get("/nfz")
async def get_nfz(x_secret: str = Header(...), db: Session = Depends(get_db)):
	if x_secret != X_SECRET:
		raise HTTPException(status_code=401, detail="Unauthorized")

	# Example response data (replace with actual data logic)
	# Fetch drone data from the external API (async HTTP request)
	try:
		data = await fetch_drones()
	except httpx.RequestError as exc:
		raise HTTPException(status_code=502, detail=f"Error contacting drones API: {exc}")
	except httpx.HTTPStatusError as exc:
		raise HTTPException(status_code=exc.response.status_code, detail=f"Drones API error: {exc.response.text}")

	# Create a database session
	violations = [] 

	# Iterate over the list of drones (adjust this if API structure differs)
	for drone in data:
		try:
			x = drone["x"]
			y = drone["y"]
			z = drone.get("z", 0)
			owner_id = drone.get("owner_id")

			if owner_id is None:
				print(f"Skipping drone due to missing owner_id: {drone}")
				continue

			owner = db.query(Owner).filter(Owner.id == owner_id).first()
			if not owner:
				# Optionally fetch owner from external API or skip
				print(f"Owner not found in DB for owner_id {owner_id}")
				continue

			owner_out = OwnerOut.from_orm(owner)

			# # Check if the drone is in the no-fly zone
			if is_in_no_fly_zone(x, y):
				print(f"Drone in restricted zone: x={x}, y={y}, z={z}, owner_id={owner_id}")

			# 	# Create a violation record with the drone's data
				violation_input = Violation(
					x=x,
					y=y,
					z=z,
					owner_id=owner_id
				)
				report_violation(violation_input, db)
				violations.append(ViolationOut(
					owner_id=owner_id,
					x=x, y=y, z=z,
					timestamp=datetime.utcnow(),
					owner=owner_out
				))

		except KeyError as e:
			print(f"Malformed drone entry skipped: missing {e} in {drone}")

	return violations

#################################################################################

def report_violation(data: ViolationInput, db: Session = Depends(get_db)):
	# 1. Try to find the owner in the database
	owner = db.query(Owner).filter(Owner.id == data.owner_id).first()

	# 2. If not found, fetch from external API
	if not owner:
		owner_data = fetch_owner(data.owner_id)
		if not owner_data:
			raise HTTPException(status_code=404, detail="Owner not found")

		# 3. Create and save the owner
		owner = Owner(
			id=data.owner_id,
			first_name=owner_data["first_name"],
			last_name=owner_data["last_name"],
			email=owner_data["email"],
			phone_number=owner_data["phone_number"],
			social_security_number=owner_data["social_security_number"],
			purchased_at=owner_data["purchased_at"]
		)
		db.add(owner)
		db.commit()

	# 4. Create and save the violation
	violation = Violation(
		owner_id=data.owner_id,
		x=data.x,
		y=data.y,
		z=data.z,
		timestamp=datetime.utcnow()
	)
	db.add(violation)
	db.commit()

	return {"message": "Violation recorded"}
################################################################################