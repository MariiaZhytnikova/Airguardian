# from sqlalchemy.orm import Session, sessionmaker
# from fastapi import Depends, HTTPException
# from datetime import datetime
# from app.drone_db import SessionLocal

# from app.model import Owner, Violation
# from app.schemas import ViolationInput
# from app.fetcher import fetch_owner

# # Function to check if a drone is in the no-fly zone
# def is_in_no_fly_zone(x: float, y: float) -> bool:
# 	return x ** 2 + y ** 2 <= 1000 ** 2

# def get_db():
# 	db = SessionLocal()
# 	try:
# 		yield db
# 	finally:
# 		db.close()

# #def report_violation(data: ViolationInput, db: Session = Depends(get_db)):
# def report_violation(data, db: Session):
# 	# 1. Try to find the owner in the database
# 	owner = db.query(Owner).filter(Owner.id == str(data.owner_id)).first()

# 	# 2. If not found, fetch from external API
# 	if not owner:
# 		owner_data = fetch_owner(data.owner_id)
# 		if not owner_data:
# 			raise HTTPException(status_code=404, detail="Owner not found")

# 		# 3. Create and save the owner
# 		owner = Owner(
# 			id=data.owner_id,
# 			first_name=owner_data["first_name"],
# 			last_name=owner_data["last_name"],
# 			email=owner_data["email"],
# 			phone_number=owner_data["phone_number"],
# 			social_security_number=owner_data["social_security_number"],
# 			purchased_at=owner_data["purchased_at"]
# 		)
# 		db.add(owner)
# 		db.commit()

# 	# 4. Create and save the violation
# 	violation = Violation(
# 		drone_id=data.drone_id,
# 		owner_id=data.owner_id,
# 		x=data.x,
# 		y=data.y,
# 		z=data.z,
# 		timestamp=datetime.utcnow()
# 	)
# 	db.add(violation)
# 	db.commit()

# 	return {"message": "Violation recorded"}

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from datetime import datetime, timezone

from app.drone_db import SessionLocal
from app.model import Owner, Violation
from app.fetcher import fetch_owner


def is_in_no_fly_zone(x: float, y: float) -> bool:
    """Return True if the drone is inside the no-fly zone radius."""
    return x ** 2 + y ** 2 <= 1000 ** 2


def get_db():
    """FastAPI dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def report_violation(data, db: Session):
    """
    Record a violation in the database.
    - Fetch owner if not found locally
    - Create violation entry
    """

    # -----------------------------------------
    # 1. Check if owner exists locally
    # -----------------------------------------
    owner = db.query(Owner).filter(Owner.id == str(data.owner_id)).first()

    # -----------------------------------------
    # 2. If not found -> fetch from external API
    # -----------------------------------------
    if not owner:
        owner_data = fetch_owner(data.owner_id)
        if not owner_data:
            raise HTTPException(status_code=404, detail="Owner not found")

        # Parse purchased_at safely
        purchased_at = owner_data.get("purchased_at")
        if isinstance(purchased_at, str):
            try:
                purchased_at = datetime.fromisoformat(purchased_at)
            except ValueError:
                purchased_at = None

        owner = Owner(
            id=data.owner_id,
            first_name=owner_data["first_name"],
            last_name=owner_data["last_name"],
            email=owner_data["email"],
            phone_number=owner_data["phone_number"],
            social_security_number=owner_data["social_security_number"],
            purchased_at=purchased_at,
        )

        db.add(owner)

    # -----------------------------------------
    # 3. Create violation
    # -----------------------------------------
    violation = Violation(
        drone_id=data.drone_id,
        owner_id=data.owner_id,
        x=data.x,
        y=data.y,
        z=data.z,
        timestamp=datetime.now(timezone.utc),
    )

    db.add(violation)

    # -----------------------------------------
    # 4. Commit changes ONCE for performance
    # -----------------------------------------
    db.commit()

    return {"message": "Violation recorded"}
