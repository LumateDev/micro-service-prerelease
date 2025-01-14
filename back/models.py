from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str