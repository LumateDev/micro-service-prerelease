from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String(64), nullable=False)  # Хэш пароля (SHA-256)
    created_at = Column(DateTime, server_default=func.now())

    # Связи с таблицами записей на экзамены и пересдачи
    exam_enrollments = relationship("Enrolments_Exams", back_populates="user")
    retake_enrollments = relationship("Enrolments_Retake", back_populates="user")


# Модель экзамена
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    # Связь с таблицей записей на экзамены
    exam_enrollments = relationship("Enrolments_Exams", back_populates="exam")


# Модель пересдачи
class Retake(Base):
    __tablename__ = "retakes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    # Связь с таблицей записей на пересдачи
    retake_enrollments = relationship("Enrolments_Retake", back_populates="retake")


# Модель записи на экзамен
class Enrolments_Exams(Base):
    __tablename__ = "enrolments_exams"

    email = Column(String, ForeignKey("users.email"), primary_key=True)
    date = Column(DateTime, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), primary_key=True)
    type = Column(String, nullable=False)

    # Связи с таблицами пользователей и экзаменов
    user = relationship("User", back_populates="exam_enrollments")
    exam = relationship("Exam", back_populates="exam_enrollments")


# Модель записи на пересдачу
class Enrolments_Retake(Base):
    __tablename__ = "enrolments_retake"

    email = Column(String, ForeignKey("users.email"), primary_key=True)
    date = Column(DateTime, nullable=False)
    retake_id = Column(Integer, ForeignKey("retakes.id"), primary_key=True)
    type = Column(String, nullable=False)

    # Связи с таблицами пользователей и пересдач
    user = relationship("User", back_populates="retake_enrollments")
    retake = relationship("Retake", back_populates="retake_enrollments")
