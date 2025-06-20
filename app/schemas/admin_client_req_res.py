from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import date
from .base import *
from .common import GenderModel
from .fee_schema import PaymentWindow

class PrevResultsModel(BaseModel):
    percentage:float
    year:int
    board:Optional[str]

class WeakSubjectsModel(BaseModel):
    subject:str
    max_marks:int
    marks_obtained:int
    details:Optional[str]

class CoachingModes(str, Enum):
    ONLINE='online'
    OFFLINE='offline'
    PERSONALISED_ONE_ON_ONE='personalised_one_on_one'

class FeeTypes(str, Enum):
    ONE_TIME='one-time'
    TWO_TIME='two-time'
    FOUR_TIME='four-time'

class Student(BaseModelWithConfig):
    name:str
    email:EmailStr
    contact_number: str = Field(..., min_length=10, max_length=10, pattern="^[0-9]{10}$")
    address:str
    gender:GenderModel
    guardian_parent_name:str
    dob:date
    grade:int                                 # student's class
    school_name:str
    coaching_mode:CoachingModes
    fee_type:FeeTypes                          # FEE01, FEE02, FEE04
    prev_year_results:PrevResultsModel
    weak_subjects: Optional[List[WeakSubjectsModel]]
    date_joined:date

class Installments(BaseModel):
    installment_number:int
    total_installment_amount_to_pay:int
    payment_window:PaymentWindow
    payment_status:bool

class PaymentType(str, Enum):
    ONE_TIME='one_time'
    TWO_TIME='two_time'
    FOUR_TIME='four_time'

class Modes(str, Enum):
    ONLINE='online'
    OFFLINE='offline'

class DiscountAppliedBaseModel(BaseModel):
    payment_type_discount:float
    coaching_mode_discount:float
    scholarship_discount:float

class DiscountResponseBase(BaseModel):
    total_discount:float
    discounts_applied:DiscountAppliedBaseModel

class TeacherProfile(BaseModelWithConfig):
    name:str
    email:EmailStr
    contact_number: str = Field(..., min_length=10, max_length=10, pattern="^[0-9]{10}$")
    address:str
    teaching_experience:int
    qualifications:List[str]
    achievements:List[str]
    date_joined:datetime

# *************************** Request Models Main ***************************

class AddNewStudentRequest(BaseModel):
    userID:str
    userPassword:str
    studentProfile:Student
    selectedSubjects:List[str]
    installments:List[Installments]

class CalculateCourseFeeRequest(BaseModel):
    grade:int
    date_joined:datetime
    prev_year_results:PrevResultsModel
    selectedSubjects:List[str]
    payment_type:PaymentType
    coaching_mode:Modes

class AddNewTeacherRequest(BaseModel):
    userID:str
    userPassword:str
    teacherProfile:TeacherProfile
    teachingSubjects:Dict[int, List[str]]

# *************************** Response Models Main ***************************

class CalculateCourseFeeResponse(BaseModel):
    admission_fee:float
    fixed_amt:float
    tuition_fee:float
    discount:DiscountResponseBase
    total_fee:float
    final_fee:float

