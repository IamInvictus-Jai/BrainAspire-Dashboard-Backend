from .base import *
from pydantic import Field, EmailStr
from enum import Enum
from typing import List
from datetime import datetime

# **************************** Teachers Model ****************************
class Teachers(BaseModelWithConfig):
    id:PyObjectId = Field(..., alias="_id")         # pass the teacher objectId to the database
    name:str
    email:EmailStr
    contact_number: str = Field(..., min_length=10, max_length=10, pattern="^[0-9]{10}$")
    address:str
    teaching_experience:int
    qualifications:List[str]
    achievements:List[str]
    date_joined:datetime
