from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from enum import Enum

class PyObjectId(ObjectId):
    """Custom ObjectId validator for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v, info):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


# Shared config for all models
class BaseModelWithConfig(BaseModel):
    model_config = {
        "json_encoders": {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        },
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# class GenderModel(str, Enum):
#     MALE='male'
#     FEMALE='female'
#     OTHER='other'