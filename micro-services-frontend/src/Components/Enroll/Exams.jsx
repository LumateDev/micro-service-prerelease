import React from "react";
import ExamCard from "../ExamCard/ExamCard";
import "./exams.css";
import "../../style/gridLayout.css";

const Exams = () => {
    // Пример данных о доступных экзаменах
    const availableExams = [
        { id: 1, name: "Математика", date: "25.10.2023, 10:00", description: "Экзамен по математике" },
        { id: 2, name: "Физика", date: "27.10.2023, 14:00", description: "Экзамен по физике" },
    ];

    const handleEnroll = (examId) => {
        console.log("Записаться на экзамен:", examId);
    };

    return (
        <div className="course-enroll-container">
            <div className="exams-title">
                Предстоящие экзамены
            </div>
            <div className="grid-container">
                {availableExams.map((exam) => (
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

export default Exams;