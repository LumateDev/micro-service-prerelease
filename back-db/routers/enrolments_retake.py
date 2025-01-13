from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import EnrolmentRetakeCreate, EnrolmentRetakeResponse
from crud import create_enrolment_retake, get_retake_by_id, get_enrolment_retake_by_email_and_retake_id
from database import get_db

router = APIRouter()

@router.post("/", response_model=EnrolmentRetakeResponse)
async def create_enrolment_retake_endpoint(enrolment: EnrolmentRetakeCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт запись на пересдачу."""
    # Проверяем, существует ли пересдача
    retake = await get_retake_by_id(db, enrolment.retake_id)
    if not retake:
        raise HTTPException(status_code=404, detail="Пересдача не найдена")

    # Проверяем, существует ли уже запись на эту пересдачу с таким же email
    existing_enrolment = await get_enrolment_retake_by_email_and_retake_id(
        db, enrolment.email, enrolment.retake_id
    )
    if existing_enrolment:
        raise HTTPException(status_code=400, detail="Запись на эту пересдачу уже существует")

    # Создаём запись на пересдачу
    db_enrolment = await create_enrolment_retake(db, enrolment)
    return db_enrolment