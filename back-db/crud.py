from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, Exam, Retake, Enrolments_Exams, Enrolments_Retake
from schemas import UserCreate, ExamCreate, RetakeCreate, EnrolmentExamCreate, EnrolmentRetakeCreate, UserUpdate


async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    if user.name:
        db_user.name = user.name
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.password = user.password

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    await db.delete(db_user)
    await db.commit()
    return db_user


async def create_exam(db: AsyncSession, exam: ExamCreate):
    db_exam = Exam(name=exam.name, date=exam.date)
    db.add(db_exam)
    await db.commit()
    await db.refresh(db_exam)
    return db_exam


async def get_exam_by_id(db: AsyncSession, exam_id: int):
    result = await db.execute(select(Exam).filter(Exam.id == exam_id))
    return result.scalars().first()


async def get_exams(db: AsyncSession):
    result = await db.execute(select(Exam))
    return result.scalars().all()


async def create_retake(db: AsyncSession, retake: RetakeCreate):
    db_retake = Retake(name=retake.name, date=retake.date)
    db.add(db_retake)
    await db.commit()
    await db.refresh(db_retake)
    return db_retake


async def get_retake_by_id(db: AsyncSession, retake_id: int):
    result = await db.execute(select(Retake).filter(Retake.id == retake_id))
    return result.scalars().first()


async def get_retakes(db: AsyncSession):
    result = await db.execute(select(Retake))
    return result.scalars().all()


async def create_enrolment_exam(db: AsyncSession, enrolment: EnrolmentExamCreate):
    db_enrolment = Enrolments_Exams(
        email=enrolment.email,
        exam_id=enrolment.exam_id,
        type=enrolment.type,
        date=enrolment.date
    )
    db.add(db_enrolment)
    await db.commit()
    await db.refresh(db_enrolment)
    return db_enrolment


async def get_enrolment_exam_by_email_and_exam_id(db: AsyncSession, email: str, exam_id: int):
    """Проверяет, существует ли запись на экзамен с указанным email и exam_id."""
    result = await db.execute(
        select(Enrolments_Exams).filter(
            Enrolments_Exams.email == email,
            Enrolments_Exams.exam_id == exam_id
        )
    )
    return result.scalars().first()


async def create_enrolment_retake(db: AsyncSession, enrolment: EnrolmentRetakeCreate):
    db_enrolment = Enrolments_Retake(
        email=enrolment.email,
        retake_id=enrolment.retake_id,
        type=enrolment.type,
        date=enrolment.date
    )
    db.add(db_enrolment)
    await db.commit()
    await db.refresh(db_enrolment)
    return db_enrolment


async def get_enrolment_retake_by_email_and_retake_id(db: AsyncSession, email: str, retake_id: int):
    """Проверяет, существует ли запись на пересдачу с указанным email и retake_id."""
    result = await db.execute(
        select(Enrolments_Retake).filter(
            Enrolments_Retake.email == email,
            Enrolments_Retake.retake_id == retake_id
        )
    )
    return result.scalars().first()


async def delete_enrolment_exam(db: AsyncSession, email: str, exam_id: int):
    """Удаляет запись на экзамен."""
    enrolment = await get_enrolment_exam_by_email_and_exam_id(db, email, exam_id)
    if not enrolment:
        return None

    await db.delete(enrolment)
    await db.commit()
    return enrolment


async def delete_enrolment_retake(db: AsyncSession, email: str, retake_id: int):
    """Удаляет запись на пересдачу."""
    enrolment = await get_enrolment_retake_by_email_and_retake_id(db, email, retake_id)
    if not enrolment:
        return None

    await db.delete(enrolment)
    await db.commit()
    return enrolment
