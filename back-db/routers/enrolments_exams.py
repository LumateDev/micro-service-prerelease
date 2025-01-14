from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
from schemas import EnrolmentExamCreate, EnrolmentExamResponse
from crud import create_enrolment_exam, get_exam_by_id, get_enrolment_exam_by_email_and_exam_id, delete_enrolment_exam
from database import get_db
from models import Enrolments_Exams

router = APIRouter()


@router.post("/", response_model=EnrolmentExamResponse)
async def create_enrolment_exam_endpoint(enrolment: EnrolmentExamCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт запись на экзамен."""
    exam = await get_exam_by_id(db, enrolment.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Экзамен не найден")

    existing_enrolment = await get_enrolment_exam_by_email_and_exam_id(
        db, enrolment.email, enrolment.exam_id
    )
    if existing_enrolment:
        raise HTTPException(status_code=400, detail="Запись на этот экзамен уже существует")

    db_enrolment = await create_enrolment_exam(db, enrolment)
    return db_enrolment


@router.get("/", response_model=list[EnrolmentExamResponse])
async def list_enrolments_exams(email: str = Query(None), db: AsyncSession = Depends(get_db)):
    """Получает список записей на экзамены."""
    query = select(Enrolments_Exams).options(joinedload(Enrolments_Exams.exam))
    if email:
        query = query.filter(Enrolments_Exams.email == email)
    result = await db.execute(query)
    enrolments = result.scalars().all()

    response = []
    for enrolment in enrolments:
        response.append({
            "email": enrolment.email,
            "exam_id": enrolment.exam_id,
            "type": enrolment.type,
            "date": enrolment.date,
            "exam_name": enrolment.exam.name
        })

    return response


@router.delete("/", response_model=dict)
async def delete_enrolment_exam_endpoint(
        email: str = Query(..., description="Email пользователя"),
        exam_id: int = Query(..., description="ID экзамена"),
        db: AsyncSession = Depends(get_db)
):
    """Удаляет запись на экзамен."""
    enrolment = await delete_enrolment_exam(db, email, exam_id)
    if not enrolment:
        raise HTTPException(status_code=404, detail="Запись на экзамен не найдена")

    return {"message": "Запись на экзамен успешно удалена"}
