import React, { useState, useEffect, useContext, useCallback } from "react";
import ExamCard from "../Components/ExamCard/ExamCard";
import "../Components/Enroll/exams.css";
import "../style/gridLayout.css";
import { AuthContext } from "../Context/AuthContext";
import { fetchExams, enrollExam, cancelExam, fetchEnrolledExams } from "../api/api";

const CourseEnrollPage = () => {
    const [availableExams, setAvailableExams] = useState([]);
    const [enrolledExams, setEnrolledExams] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { isAuthenticated, userEmail } = useContext(AuthContext);

    const fetchEnrolledExamsData = useCallback(async () => {
        try {
            const exams = await fetchEnrolledExams(userEmail);
            setEnrolledExams(exams.map(enrolment => enrolment.exam_id));
        } catch (error) {
            console.error("Ошибка при загрузке записей на экзамены:", error);
        }
    }, [userEmail]);

    const fetchExamsData = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const exams = await fetchExams();
            setAvailableExams(exams);
        } catch (error) {
            setError("Не удалось загрузить экзамены. Попробуйте снова.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isAuthenticated) {
            fetchExamsData();
            fetchEnrolledExamsData();
        }
    }, [isAuthenticated, fetchExamsData, fetchEnrolledExamsData]);

    const filteredExams = availableExams.filter(
        exam => !enrolledExams.includes(exam.id)
    );


    const handleEnroll = async (examId) => {
        if (!isAuthenticated) {
            alert("Для записи на экзамен необходимо авторизоваться.");
            return;
        }

        try {
            await enrollExam(userEmail, examId);
            alert("Вы успешно записались на экзамен!");
            setEnrolledExams([...enrolledExams, examId]);
        } catch (error) {
            alert("Не удалось записаться на экзамен. Попробуйте снова.");
            console.error(error);
        }
    };

    const handleCancel = async (examId) => {
        try {
            await cancelExam(userEmail, examId);
            alert("Запись на экзамен отменена.");
            setEnrolledExams(enrolledExams.filter(id => id !== examId));
        } catch (error) {
            alert("Не удалось отменить запись на экзамен.");
            console.error(error);
        }
    };

    return (
        <div className="course-enroll-container">
            <div className="exams-title">Предстоящие экзамены</div>
            {loading && <div>Загрузка...</div>}
            {error && <div className="error-message">{error}</div>}
            <div className="grid-container">
                {filteredExams.map((exam) => (
                    <ExamCard
                        key={exam.id}
                        exam={exam}
                        onEnroll={() => handleEnroll(exam.id)}
                        onCancel={() => handleCancel(exam.id)}
                        isEnrolled={enrolledExams.includes(exam.id)}
                    />
                ))}
            </div>
        </div>
    );
};

export default CourseEnrollPage;