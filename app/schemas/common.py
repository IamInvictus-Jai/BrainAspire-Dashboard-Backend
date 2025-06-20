from pydantic import BaseModel, Field
from .base import *
from typing import Optional, List, Dict
from datetime import date


# used for distinguising between admin, teacher and student. Only teacher and admin will be added in this table
class Roles(str, Enum):
    ADMIN='admin'
    TEACHER='teacher'
    DEVELOPER='developer'

class UserRoles(BaseModelWithConfig):
    id:PyObjectId = Field(..., alias="_id")  # pass the user objectId to the database
    role:Roles = Field(default=Roles.TEACHER)


# **************************** Subjects Model ****************************
class Subjects(BaseModelWithConfig):
    id:str = Field(..., alias="_id")  # Use Unique Subject Code; ex: ENG006, MATH007
    name:str
    grade:int                          # student's class

class GenderModel(str, Enum):
    MALE='male'
    FEMALE='female'
    OTHER='other'

# **************************** Students Subject Mapping Model ****************************
class StudentsSubjectsMapping(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    studentID:PyObjectId = Field(..., alias="studentID")
    subjectID:PyObjectId = Field(..., alias="subjectID")

# **************************** Teacher Subject Mapping Model ****************************
class TeachersSubjectMapping(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    teacherID:PyObjectId = Field(..., alias="teacherID")
    subjectID:PyObjectId = Field(..., alias="subjectID")

# **************************** Monthly Performance Tracker ****************************
class AttendanceModel(BaseModel):
    total_classes:int
    attended_classes:int
    dates_of_absence:List[date]

class RemarksModel(BaseModel):
    teacherID:PyObjectId = Field(..., alias="teacherID")
    title:str
    remarks:str
    timestamp:datetime


class MonthlyPerformanceTracker(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    studentID:PyObjectId = Field(default_factory=PyObjectId, alias="studentID")
    grade:int
    subjectID:str = Field(..., alias="subjectID")
    monthly_remarks:Dict[str, RemarksModel] = Field(default_factory=dict)                                   # key maps to month number, mongodb always stores keys as str
    monthly_attendance:Dict[str, AttendanceModel] = Field(default_factory=dict)                             # key maps to month number, mongodb always stores keys as str
    year_batch:int

