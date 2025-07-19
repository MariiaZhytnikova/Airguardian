from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from pydantic import BaseModel
from datetime import datetime
from typing import List

########### OWN ##########################
from utils import fetch_owner
from drone_db import SessionLocal, engine
from schemas import ViolationOut
from model import Owner, Violation, Base
####################################

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

@app.get("/violations", response_model=List[ViolationOut])
def list_violations(db: Session = Depends(get_db)):
	violations = db.query(Violation).options(joinedload(Violation.owner)).all()
	return violations

class ViolationInput(BaseModel):
	owner_id: str
	x: float
	y: float
	z: float

########################################################################
#################################################################################
@app.post("/violations")
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