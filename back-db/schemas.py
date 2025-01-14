from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ExamCreate(BaseModel):
    name: str
    date: str

    @validator("date")
    def parse_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date()


class ExamResponse(BaseModel):
    id: int
    name: str
    date: str

    @validator("date", pre=True)
    def format_date(cls, value):
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        return value

    class Config:
        from_attributes = True


class RetakeCreate(BaseModel):
    name: str
    date: str

    @validator("date")
    def parse_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date()


class RetakeResponse(BaseModel):
    id: int
    name: str
    date: str

    @validator("date", pre=True)
    def format_date(cls, value):
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        return value

    class Config:
        from_attributes = True


class EnrolmentExamCreate(BaseModel):
    email: EmailStr
    exam_id: int
    type: str
    date: str

    @validator("date")
    def parse_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date()


class EnrolmentExamResponse(BaseModel):
    email: EmailStr
    exam_id: int
    type: str
    date: str
    exam_name: Optional[str] = None

    @validator("date", pre=True)
    def format_date(cls, value):
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        return value

    class Config:
        from_attributes = True


class EnrolmentRetakeCreate(BaseModel):
    email: EmailStr
    retake_id: int
    type: str
    date: str

    @validator("date")
    def parse_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date()


class EnrolmentRetakeResponse(BaseModel):
    email: EmailStr
    retake_id: int
    type: str
    date: str
    retake_name: Optional[str] = None

    @validator("date", pre=True)
    def format_date(cls, value):
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        return value

    class Config:
        from_attributes = True
