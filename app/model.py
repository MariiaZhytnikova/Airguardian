from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.drone_db import Base

class Owner(Base):
	__tablename__ = "owners"
	id = Column(String, primary_key=True, index=True)
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String)
	phone_number = Column(String)
	social_security_number = Column(String)
	purchased_at = Column(String)

	violations = relationship("Violation", back_populates="owner")

class Violation(Base):
	__tablename__ = "violations"
	id = Column(Integer, primary_key=True, index=True)
	drone_id = Column(String)
	owner_id = Column(String, ForeignKey("owners.id"))
	x = Column(Float)
	y = Column(Float)
	z = Column(Float)
	timestamp = Column(DateTime)

	owner = relationship("Owner", back_populates="violations")