from .base import *
from pydantic import Field, EmailStr
from enum import Enum
from datetime import date
from typing import Optional, List
from .common import GenderModel

class Modes(str, Enum):
    ONLINE='online'
    OFFLINE='offline'
    PERSONALISED_ONE_ON_ONE='personalised_one_on_one'

class CoachingModes(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name:Modes

class PrevResultsModel(BaseModel):
    percentage:float
    year:int
    board:str = Field(default="CBSE")

class WeakSubjectsModel(BaseModel):
    subject:str
    max_marks:int
    marks_obtained:int
    details:Optional[str]

class Students(BaseModelWithConfig):
    id:PyObjectId = Field(..., alias="_id")  # pass the user objectId to the database
    name:str
    email:EmailStr
    contact_number: str = Field(..., min_length=10, max_length=10, pattern="^[0-9]{10}$")
    address:str
    gender:GenderModel
    guardian_parent_name:str
    dob:datetime
    grade:int                                 # student's class
    school_name:str
    coaching_modeID:PyObjectId = Field(default_factory=PyObjectId, alias="coaching_modeID")
    fee_typeID:str                          # FEE01, FEE02, FEE04
    prev_year_results:PrevResultsModel
    weak_subjects: Optional[List[WeakSubjectsModel]]
    date_joined:datetime