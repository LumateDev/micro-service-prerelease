from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import RetakeCreate, RetakeResponse
from crud import create_retake, get_retakes
from database import get_db

router = APIRouter()


@router.post("/", response_model=RetakeResponse)
async def create_retake_endpoint(retake: RetakeCreate, db: AsyncSession = Depends(get_db)):
    db_retake = await create_retake(db, retake)
    if not db_retake:
        raise HTTPException(status_code=400, detail="Retake could not be created")
    return db_retake


@router.get("/", response_model=list[RetakeResponse])
async def list_retakes(db: AsyncSession = Depends(get_db)):
    return await get_retakes(db)
