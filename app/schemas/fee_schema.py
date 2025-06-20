from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Optional
from datetime import date
from .base import *


class FeeTypeModel(BaseModel):
    label: str
    installments: int
    notes: str

class FeeTypeConfigurations(BaseModelWithConfig):
    id: str = Field(default_factory="fee_type", alias="_id")
    types: Dict[str, FeeTypeModel]

# **************************** Fees Tracker Model ****************************
class PaymentWindow(BaseModel):
    start_date:datetime
    end_date:datetime

class Installments(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    studentID:PyObjectId = Field(..., alias="studentID")
    installment_number:int
    total_installment_amount_to_pay:int
    amount_paid:int=0
    payment_window:PaymentWindow                         # key maps to start and end, values are the dates
    date_of_payment_done:date=Field(default=None)        # None if not paid
    payment_status:bool

class FeeStructureModel(BaseModel):
    admission_fee: int
    fixed_amt: int
    monthly_fee: int
    course_duration: int

class FeeConfigurations(BaseModelWithConfig):
    id: str = Field(default_factory="course_fee", alias="_id")
    fees: Dict[str, FeeStructureModel]
    subject_preference_fee: Dict[str, int]

class DiscountConfigurations(BaseModelWithConfig):
    id: str = Field(default_factory="discount", alias="_id")
    payment_type_discount: Dict[str, int]
    coaching_mode_discount: Dict[str, int]
    scholarship_discount: Dict[str, int]