# from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
# from sqlalchemy.orm import relationship
# import datetime

# from app.drone_db import Base

# class Owner(Base):
# 	__tablename__ = "owners"
# 	id = Column(String, primary_key=True, index=True)
# 	first_name = Column(String)
# 	last_name = Column(String)
# 	email = Column(String)
# 	phone_number = Column(String)
# 	social_security_number = Column(String)
# 	purchased_at = Column(String)

# 	violations = relationship("Violation", back_populates="owner")

# class Violation(Base):
# 	__tablename__ = "violations"
# 	id = Column(Integer, primary_key=True, index=True)
# 	drone_id = Column(String)
# 	owner_id = Column(String, ForeignKey("owners.id"))
# 	x = Column(Float)
# 	y = Column(Float)
# 	z = Column(Float)
# 	timestamp = Column(DateTime)

# 	owner = relationship("Owner", back_populates="violations")

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.drone_db import Base


class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200))
    phone_number = Column(String(50))
    social_security_number = Column(String(50))

    # If this is a date/time, use DateTime instead of String
    purchased_at = Column(DateTime(timezone=True), nullable=True)

    # One-to-many relationship
    violations = relationship(
        "Violation",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(String(100))
    owner_id = Column(String, ForeignKey("owners.id"))
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    owner = relationship(
        "Owner",
        back_populates="violations"
    )
