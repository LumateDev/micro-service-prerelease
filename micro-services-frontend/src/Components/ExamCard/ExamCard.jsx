import React from "react";
import "./examCard.css";

const ExamCard = ({ exam, onEnroll, onCancel }) => {
    return (
        <div className="exam-card">
            <h3>{exam.name}</h3>
            <p>Дата: {exam.date}</p>
            {exam.status && <p>Статус: {exam.status}</p>}
            {exam.description && <p>{exam.description}</p>}
            {exam.reason && <p>Причина: {exam.reason}</p>}
            <div className="actions">
                {onEnroll && (
                    <button className="enroll-button" onClick={onEnroll}>
                        Записаться
                    </button>
                )}
                {onCancel && (
                    <button className="cancel-button" onClick={onCancel}>
                        Отменить запись
                    </button>
                )}
            </div>
        </div>
    );
};

export default ExamCard;