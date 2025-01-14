from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, exams, retakes, users, enrolments_exams, enrolments_retake
from database import engine, Base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(exams.router, prefix="/exams", tags=["exams"])
app.include_router(retakes.router, prefix="/retakes", tags=["retakes"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(enrolments_exams.router, prefix="/enrolments-exams", tags=["enrolments-exams"])
app.include_router(enrolments_retake.router, prefix="/enrolments-retake", tags=["enrolments-retake"])

# Создаём таблицы в базе данных (если их нет)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)