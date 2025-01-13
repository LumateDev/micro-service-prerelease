from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import EnrolmentExamCreate, EnrolmentExamResponse
from crud import create_enrolment_exam, get_exam_by_id, get_enrolment_exam_by_email_and_exam_id
from database import get_db

router = APIRouter()



@router.post("/", response_model=EnrolmentExamResponse)
async def create_enrolment_exam_endpoint(enrolment: EnrolmentExamCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт запись на экзамен."""
    # Проверяем, существует ли экзамен
    exam = await get_exam_by_id(db, enrolment.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Экзамен не найден")

    # Проверяем, существует ли уже запись на этот экзамен с таким же email
    existing_enrolment = await get_enrolment_exam_by_email_and_exam_id(
        db, enrolment.email, enrolment.exam_id
    )
    if existing_enrolment:
        raise HTTPException(status_code=400, detail="Запись на этот экзамен уже существует")

    # Создаём запись на экзамен
    db_enrolment = await create_enrolment_exam(db, enrolment)
    return db_enrolment
