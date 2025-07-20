from sqlalchemy.orm import Session, sessionmaker, Session
from fastapi import Depends, HTTPException
from datetime import datetime
from drone_db import SessionLocal  # Added this import

from model import Owner, Violation
from schemas import ViolationInput
from fetcher import fetch_owner

# Function to check if a drone is in the no-fly zone

def is_in_no_fly_zone(x: float, y: float) -> bool:
	return x ** 2 + y ** 2 <= 1000 ** 2

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#def report_violation(data: ViolationInput, db: Session = Depends(get_db)):
def report_violation(data, db: Session):
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
