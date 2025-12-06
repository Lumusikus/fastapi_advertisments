from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum



class AdvertisementBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class Advertisement(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.user


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str