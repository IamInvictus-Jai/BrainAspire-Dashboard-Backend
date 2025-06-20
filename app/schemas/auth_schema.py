from pydantic import BaseModel, Field
from app.schemas.base import PyObjectId, BaseModelWithConfig
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    user_id: str
    password: str

class UserInDB(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    hashed_password: str
    last_login: Optional[datetime]

class Auth(BaseModelWithConfig):
    id:PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userID:str
    hashed_pswd:str
    is_active:bool
    last_login:datetime