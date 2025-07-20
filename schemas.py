from pydantic import BaseModel
from datetime import datetime

class ViolationInput(BaseModel):
	owner_id: str
	x: float
	y: float
	z: float

	class Config:
		from_attributes = True

class OwnerOut(BaseModel):
	first_name: str
	last_name: str
	social_security_number: str
	phone_number: str

	class Config:
		from_attributes = True

class ViolationOut(BaseModel):
	owner_id: str
	timestamp: datetime
	x: float
	y: float
	z: float
	owner: OwnerOut

	class Config:
		from_attributes = True

