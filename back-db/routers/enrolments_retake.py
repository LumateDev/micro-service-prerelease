from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
from schemas import EnrolmentRetakeCreate, EnrolmentRetakeResponse
from crud import create_enrolment_retake, get_retake_by_id, get_enrolment_retake_by_email_and_retake_id, \
    delete_enrolment_retake
from database import get_db
from models import Enrolments_Retake

router = APIRouter()


@router.post("/", response_model=EnrolmentRetakeResponse)
async def create_enrolment_retake_endpoint(enrolment: EnrolmentRetakeCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт запись на пересдачу."""
    retake = await get_retake_by_id(db, enrolment.retake_id)
    if not retake:
        raise HTTPException(status_code=404, detail="Пересдача не найдена")

    existing_enrolment = await get_enrolment_retake_by_email_and_retake_id(
        db, enrolment.email, enrolment.retake_id
    )
    if existing_enrolment:
        raise HTTPException(status_code=400, detail="Запись на эту пересдачу уже существует")

    db_enrolment = await create_enrolment_retake(db, enrolment)
    return db_enrolment


@router.get("/", response_model=list[EnrolmentRetakeResponse])
async def list_enrolments_retake(email: str = Query(None), db: AsyncSession = Depends(get_db)):
    """Получает список записей на пересдачи."""
    query = select(Enrolments_Retake).options(joinedload(Enrolments_Retake.retake))
    if email:
        query = query.filter(Enrolments_Retake.email == email)
    result = await db.execute(query)
    enrolments = result.scalars().all()

    response = []
    for enrolment in enrolments:
        response.append({
            "email": enrolment.email,
            "retake_id": enrolment.retake_id,
            "type": enrolment.type,
            "date": enrolment.date,
            "retake_name": enrolment.retake.name
        })

    return response


@router.delete("/", response_model=dict)
async def delete_enrolment_retake_endpoint(
        email: str = Query(..., description="Email пользователя"),
        retake_id: int = Query(..., description="ID пересдачи"),
        db: AsyncSession = Depends(get_db)
):
    """Удаляет запись на пересдачу."""
    enrolment = await delete_enrolment_retake(db, email, retake_id)
    if not enrolment:
        raise HTTPException(status_code=404, detail="Запись на пересдачу не найдена")

    return {"message": "Запись на пересдачу успешно удалена"}
