from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, date


# Модель для регистрации пользователя
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# Модель для ответа с данными пользователя
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


# Модель для обновления данных пользователя
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


# Модель для авторизации
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Модель для экзамена
class ExamCreate(BaseModel):
    name: str
    date: str  # Принимаем строку от пользователя

    @validator("date")
    def parse_date(cls, value):
        # Преобразуем строку в объект datetime.date
        return datetime.strptime(value, "%d-%m-%Y").date()


class ExamResponse(BaseModel):
    id: int
    name: str
    date: str  # Возвращаем строку для удобства

    @validator("date", pre=True)
    def format_date(cls, value):
        # Преобразуем datetime.datetime или datetime.date в строку
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")  # Формат: год-месяц-день
        return value

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


# Модель для пересдачи
class RetakeCreate(BaseModel):
    name: str
    date: str  # Принимаем строку от пользователя

    @validator("date")
    def parse_date(cls, value):
        # Преобразуем строку в объект datetime.date
        return datetime.strptime(value, "%d-%m-%Y").date()


class RetakeResponse(BaseModel):
    id: int
    name: str
    date: str  # Возвращаем строку для удобства

    @validator("date", pre=True)
    def format_date(cls, value):
        # Преобразуем datetime.datetime или datetime.date в строку
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")  # Формат: год-месяц-день
        return value

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


# Модель для записи на экзамен
class EnrolmentExamCreate(BaseModel):
    email: EmailStr
    exam_id: int
    type: str
    date: str  # Принимаем строку от пользователя

    @validator("date")
    def parse_date(cls, value):
        # Преобразуем строку в объект datetime.date
        return datetime.strptime(value, "%d-%m-%Y").date()


class EnrolmentExamResponse(BaseModel):
    email: EmailStr
    exam_id: int
    type: str
    date: str  # Возвращаем строку для удобства

    @validator("date", pre=True)
    def format_date(cls, value):
        # Преобразуем datetime.datetime или datetime.date в строку
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")  # Формат: год-месяц-день
        return value

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy


# Модель для записи на пересдачу
class EnrolmentRetakeCreate(BaseModel):
    email: EmailStr
    retake_id: int
    type: str
    date: str  # Принимаем строку от пользователя

    @validator("date")
    def parse_date(cls, value):
        # Преобразуем строку в объект datetime.date
        return datetime.strptime(value, "%d-%m-%Y").date()


class EnrolmentRetakeResponse(BaseModel):
    email: EmailStr
    retake_id: int
    type: str
    date: str  # Возвращаем строку для удобства

    @validator("date", pre=True)
    def format_date(cls, value):
        # Преобразуем datetime.datetime или datetime.date в строку
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")  # Формат: год-месяц-день
        return value

    class Config:
        from_attributes = True  # Для совместимости с SQLAlchemy