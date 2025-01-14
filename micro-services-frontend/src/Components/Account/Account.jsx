import React, { useState, useEffect, useContext, useCallback } from "react";
import ExamCard from "../ExamCard/ExamCard";
import "./account.css";
import "../../style/gridLayout.css";
import { AuthContext } from "../../Context/AuthContext";
import { fetchEnrolledExams, fetchEnrolledRetakes, cancelExam, cancelRetake } from "../../api/api";

const Account = () => {
    const [enrolledExams, setEnrolledExams] = useState([]);
    const [enrolledRetakes, setEnrolledRetakes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errorExams, setErrorExams] = useState("");
    const [errorRetakes, setErrorRetakes] = useState("");
    const { isAuthenticated, userName, userEmail } = useContext(AuthContext);

    const fetchEnrolledExamsData = useCallback(async () => {
        setLoading(true);
        setErrorExams("");

        try {
            const exams = await fetchEnrolledExams(userEmail);
            setEnrolledExams(exams);
        } catch (error) {
            setErrorExams("Не удалось загрузить записи на экзамены. Попробуйте снова.");
        } finally {
            setLoading(false);
        }
    }, [userEmail]);

    const fetchEnrolledRetakesData = useCallback(async () => {
        setLoading(true);
        setErrorRetakes("");

        try {
            const retakes = await fetchEnrolledRetakes(userEmail);
            setEnrolledRetakes(retakes);
        } catch (error) {
            setErrorRetakes("Не удалось загрузить записи на пересдачи. Попробуйте снова.");
        } finally {
            setLoading(false);
        }
    }, [userEmail]);

    useEffect(() => {
        if (isAuthenticated) {
            fetchEnrolledExamsData();
            fetchEnrolledRetakesData();
        }
    }, [isAuthenticated, fetchEnrolledExamsData, fetchEnrolledRetakesData]);

    const handleCancelExam = async (examId) => {
        try {
            await cancelExam(userEmail, examId);
            alert("Запись на экзамен отменена.");
            setEnrolledExams(enrolledExams.filter(enrolment => enrolment.exam_id !== examId));
        } catch (error) {
            alert(error);
        }
    };

    const handleCancelRetake = async (retakeId) => {
        try {
            await cancelRetake(userEmail, retakeId);
            alert("Запись на пересдачу отменена.");
            setEnrolledRetakes(enrolledRetakes.filter(enrolment => enrolment.retake_id !== retakeId));
        } catch (error) {
            alert(error);
        }
    };

    return (
        <div className="home-container">
            <div className="user-container">
                <div className="account-info">
                    <h2>Информация об аккаунте</h2>
                    <p>Имя: {userName}</p>
                    <p>Электронная почта: {userEmail}</p>
                    <p>Статус: Студент</p>
                </div>
            </div>

            <div className="grid-container">
                <h3>Мои записи на экзамены</h3>
                {loading && <div>Загрузка...</div>}
                {errorExams && <div className="error-message">{errorExams}</div>}
                {enrolledExams.length > 0 ? (
                    enrolledExams.map((enrolment) => (
                        <ExamCard
                            key={enrolment.exam_id}
                            exam={{
                                id: enrolment.exam_id,
                                name: enrolment.exam_name,
                                date: enrolment.date,
                                description: `Тип: ${enrolment.type}`,
                            }}
                            onCancel={() => handleCancelExam(enrolment.exam_id)}
                            isEnrolled={true}
                        />
                    ))
                ) : (
                    !errorExams && <p>Вы ещё не записаны ни на один экзамен.</p>
                )}
            </div>

            <div className="grid-container">
                <h3>Мои записи на пересдачи</h3>
                {loading && <div>Загрузка...</div>}
                {errorRetakes && <div className="error-message">{errorRetakes}</div>}
                {enrolledRetakes.length > 0 ? (
                    enrolledRetakes.map((enrolment) => (
                        <ExamCard
                            key={enrolment.retake_id}
                            exam={{
                                id: enrolment.retake_id,
                                name: enrolment.retake_name,
                                date: enrolment.date,
                                description: `Тип: ${enrolment.type}`,
                            }}
                            onCancel={() => handleCancelRetake(enrolment.retake_id)}
                            isEnrolled={true}
                        />
                    ))
                ) : (
                    !errorRetakes && <p>Вы ещё не записаны ни на одну пересдачу.</p>
                )}
            </div>
        </div>
    );
};

export default Account;