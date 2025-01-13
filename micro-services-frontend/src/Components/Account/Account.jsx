
import React, { useContext } from "react";
import { AuthContext } from "../../Context/AuthContext";
import ExamCard from "../ExamCard/ExamCard";
import "./account.css";
import "../../style/gridLayout.css"
const Account = () => {


    const { userName } = useContext(AuthContext);

    // Пример данных об экзаменах
    const exams = [
        { id: 1, name: "Математика", date: "25.10.2023, 10:00", status: "Записан" },
        { id: 2, name: "Физика", date: "27.10.2023, 14:00", status: "Записан" },
    ];

    const handleCancel = (examId) => {
        console.log("Отменить запись на экзамен:", examId);
    };

    return (
        <div className="home-container">
            <div className="user-container">
                <div className="account-info">
                    <h2>Информация об аккаунте</h2>
                    <p>Имя: {userName}</p>
                    <p>Электронная почта: user@example.com</p>
                    <p>Статус: Студент</p>
                </div>

            </div>
            <div className="grid-container">
                {exams.map((exam) => (
                    <ExamCard
                        key={exam.id}
                        exam={exam}
                        onCancel={() => handleCancel(exam.id)}
                    />
                ))}
            </div>
        </div>
    );
};

export default Account;