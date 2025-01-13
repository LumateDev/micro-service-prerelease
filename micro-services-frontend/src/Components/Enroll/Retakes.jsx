import React from "react";
import ExamCard from "../ExamCard/ExamCard";
import "./retakes.css"
import "../../style/gridLayout.css"

const Retakes = () => {
    // Пример данных о пересдачах
    const retakeExams = [
        { id: 1, name: "Математика", date: "25.10.2023, 10:00", reason: "Не сдан" },
        { id: 2, name: "Физика", date: "27.10.2023, 14:00", reason: "Не сдан" },
    ];

    const handleEnroll = (examId) => {
        console.log("Записаться на пересдачу:", examId);
    };

    return (
        <div className="retake-enroll-container">
            <div className="retakes-title">
                Предстоящие пересдачи
            </div>
            <div className="grid-container">
                {retakeExams.map((exam) => (
                    <ExamCard
                        key={exam.id}
                        exam={exam}
                        onEnroll={() => handleEnroll(exam.id)}
                    />
                ))}
            </div>
        </div>
    );
};

export default Retakes;