from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import ExamCreate, ExamResponse
from crud import create_exam, get_exams
from database import get_db

router = APIRouter()


@router.post("/", response_model=ExamResponse)
async def create_exam_endpoint(exam: ExamCreate, db: AsyncSession = Depends(get_db)):
    db_exam = await create_exam(db, exam)
    if not db_exam:
        raise HTTPException(status_code=400, detail="Exam could not be created")
    return db_exam


@router.get("/", response_model=list[ExamResponse])
async def list_exams(db: AsyncSession = Depends(get_db)):
    return await get_exams(db)
