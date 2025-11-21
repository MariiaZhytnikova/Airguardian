# from pydantic import BaseModel
# from datetime import datetime

# class ViolationInput(BaseModel):
# 	drone_id: str
# 	owner_id: str
# 	x: float
# 	y: float
# 	z: float

# 	class Config:
# 		from_attributes = True

# class OwnerOut(BaseModel):
# 	first_name: str
# 	last_name: str
# 	social_security_number: str
# 	phone_number: str

# 	class Config:
# 		from_attributes = True

# class ViolationOut(BaseModel):
# 	drone_id: str
# 	timestamp: datetime
# 	x: float
# 	y: float
# 	z: float
# 	owner: OwnerOut

# 	class Config:
# 		from_attributes = True

from datetime import datetime
from pydantic import BaseModel


class ViolationInput(BaseModel):
    """Incoming violation data used internally before saving."""

    drone_id: str
    owner_id: str
    x: float
    y: float
    z: float

    class Config:
        from_attributes = True


class OwnerOut(BaseModel):
    """Owner information returned from external API or database."""

    first_name: str
    last_name: str
    social_security_number: str
    phone_number: str

    class Config:
        from_attributes = True


class ViolationOut(BaseModel):
    """Violation record returned from API including owner details."""

    drone_id: str
    timestamp: datetime
    x: float
    y: float
    z: float
    owner: OwnerOut

    class Config:
        from_attributes = True
