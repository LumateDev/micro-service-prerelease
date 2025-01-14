import React from "react";
import "./examCard.css";

const ExamCard = ({ exam, onEnroll, onCancel, isEnrolled }) => {
    return (
        <div className="exam-card">
            <h3>{exam.name}</h3>
            <p>Дата: {exam.date}</p>
            <p>{exam.type || "Описание отсутствует"}</p>
            {isEnrolled ? (
                <button onClick={onCancel} className="cancel-button">
                    Отменить запись
                </button>
            ) : (
                <button onClick={onEnroll} className="enroll-button">
                    Записаться
                </button>
            )}
        </div>
    );
};

export default ExamCard;