import React, { useState, useEffect, useContext, useCallback } from "react";
import ExamCard from "../Components/ExamCard/ExamCard";
import "../Components/Enroll/retakes.css";
import "../style/gridLayout.css";
import { AuthContext } from "../Context/AuthContext";
import { fetchRetakes, enrollRetake, cancelRetake, fetchEnrolledRetakes } from "../api/api";

const RetakeEnrollPage = () => {
    const [retakeExams, setRetakeExams] = useState([]);
    const [enrolledRetakes, setEnrolledRetakes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { isAuthenticated, userEmail } = useContext(AuthContext);

    const fetchEnrolledRetakesData = useCallback(async () => {
        try {
            const retakes = await fetchEnrolledRetakes(userEmail);
            setEnrolledRetakes(retakes.map(enrolment => enrolment.retake_id));
        } catch (error) {
            console.error("Ошибка при загрузке записей:", error);
        }
    }, [userEmail]);


    const fetchRetakesData = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const retakes = await fetchRetakes();
            setRetakeExams(retakes);
        } catch (error) {
            setError(error);
        } finally {
            setLoading(false);
        }
    }, []);


    useEffect(() => {
        if (isAuthenticated) {
            fetchRetakesData();
            fetchEnrolledRetakesData();
        }
    }, [isAuthenticated, fetchRetakesData, fetchEnrolledRetakesData]);


    const filteredRetakes = retakeExams.filter(
        retake => !enrolledRetakes.includes(retake.id)
    );

    const handleEnroll = async (retakeId) => {
        if (!isAuthenticated) {
            alert("Для записи на пересдачу необходимо авторизоваться.");
            return;
        }

        try {
            await enrollRetake(userEmail, retakeId);
            alert("Вы успешно записались на пересдачу!");
            setEnrolledRetakes([...enrolledRetakes, retakeId]);
        } catch (error) {
            alert("Не удалось записаться на пересдачу. Попробуйте снова.");
            console.error(error);
        }
    };

    const handleCancel = async (retakeId) => {
        try {
            await cancelRetake(userEmail, retakeId); // Используем функцию из api.js
            alert("Запись на пересдачу отменена.");
            setEnrolledRetakes(enrolledRetakes.filter(id => id !== retakeId));
        } catch (error) {
            alert("Не удалось отменить запись на пересдачу.");
            console.error(error);
        }
    };

    return (
        <div className="retake-enroll-container">
            <div className="retakes-title">Предстоящие пересдачи</div>
            {loading && <div>Загрузка...</div>}
            {error && <div className="error-message">{error}</div>}
            <div className="grid-container">
                {filteredRetakes.map((retake) => (
                    <ExamCard
                        key={retake.id}
                        exam={retake}
                        onEnroll={() => handleEnroll(retake.id)}
                        onCancel={() => handleCancel(retake.id)}
                        isEnrolled={enrolledRetakes.includes(retake.id)}
                    />
                ))}
            </div>
        </div>
    );
};

export default RetakeEnrollPage;