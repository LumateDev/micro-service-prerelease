from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreate, UserResponse, UserUpdate
from crud import create_user, get_users, get_user_by_id, update_user, delete_user, get_user_by_email
from database import get_db

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт нового пользователя."""
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    return await create_user(db, user)


@router.get("/", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """Получает список всех пользователей."""
    return await get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получает информацию о конкретном пользователе."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Обновляет данные пользователя."""
    db_user = await update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """Удаляет пользователя."""
    db_user = await delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user
