import React, { useState, useEffect, useContext } from "react";
import ExamCard from "../ExamCard/ExamCard";
import "./exams.css";
import "../../style/gridLayout.css";
import { AuthContext } from "../../Context/AuthContext";
import { fetchExams, enrollExam, cancelExam } from "../../api/api";

const Exams = () => {
    const [availableExams, setAvailableExams] = useState([]);
    const [enrolledExams, setEnrolledExams] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { isAuthenticated, userName } = useContext(AuthContext);

    useEffect(() => {
        if (isAuthenticated) {
            fetchExamsData();
            fetchEnrolledExamsData();
        }
    }, [isAuthenticated]);

    const fetchExamsData = async () => {
        setLoading(true);
        setError("");

        try {
            const exams = await fetchExams();
            setAvailableExams(exams);
        } catch (error) {
            setError(error);
        } finally {
            setLoading(false);
        }
    };

    const fetchEnrolledExamsData = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/enrolments-exams/?email=${userName}`);
            setEnrolledExams(response.data.map(enrolment => enrolment.exam_id));
        } catch (error) {
            console.error("Ошибка при загрузке записей:", error);
        }
    };


    const handleEnroll = async (examId) => {
        if (!isAuthenticated) {
            alert("Для записи на экзамен необходимо авторизоваться.");
            return;
        }

        try {
            await enrollExam(userName, examId);
            alert("Вы успешно записались на экзамен!");
            setEnrolledExams([...enrolledExams, examId]);
        } catch (error) {
            alert(error);
        }
    };


    const handleCancel = async (examId) => {
        try {
            await cancelExam(userName, examId);
            alert("Запись на экзамен отменена.");
            setEnrolledExams(enrolledExams.filter(id => id !== examId));
        } catch (error) {
            alert(error);
        }
    };

    return (
        <div className="course-enroll-container">
            <div className="exams-title">Предстоящие экзамены</div>
            {loading && <div>Загрузка...</div>}
            {error && <div className="error-message">{error}</div>}
            <div className="grid-container">
                {availableExams.map((exam) => (
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

export default Exams;