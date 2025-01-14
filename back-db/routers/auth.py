from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreate, UserResponse, UserLogin
from crud import create_user, get_user_by_email
from database import get_db
from hashlib import sha256

router = APIRouter()


@router.post("/registration", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    hashed_password = sha256(user.password.encode()).hexdigest()
    user.password = hashed_password

    return await create_user(db, user)


@router.post("/authorization", response_model=UserResponse)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    hashed_password = sha256(user.password.encode()).hexdigest()
    if db_user.password != hashed_password:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    return db_user
