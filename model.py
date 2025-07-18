class Owner(Base):
	__tablename__ = "owners"

	id = Column(String, primary_key=True)  # Use the given UUID
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String)
	phone_number = Column(String)
	social_security_number = Column(String)
	purchased_at = Column(DateTime)

class Violation(Base):
	__tablename__ = "violations"

	id = Column(Integer, primary_key=True, index=True)
	drone_id = Column(String)
	timestamp = Column(DateTime)
	x = Column(Float)
	y = Column(Float)
	z = Column(Float)
	owner_id = Column(String, ForeignKey("owners.id"))
