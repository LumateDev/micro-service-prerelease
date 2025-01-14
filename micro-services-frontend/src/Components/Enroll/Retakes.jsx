import React, { useState, useEffect, useContext } from "react";
import ExamCard from "../ExamCard/ExamCard";
import "./retakes.css";
import "../../style/gridLayout.css";
import { AuthContext } from "../../Context/AuthContext";
import { fetchRetakes, enrollRetake, cancelRetake } from "../../api/api";

const Retakes = () => {
    const [retakeExams, setRetakeExams] = useState([]);
    const [enrolledRetakes, setEnrolledRetakes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { isAuthenticated, userName } = useContext(AuthContext);

    useEffect(() => {
        if (isAuthenticated) {
            fetchRetakesData();
            fetchEnrolledRetakesData();
        }
    }, [isAuthenticated]);


    const fetchRetakesData = async () => {
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
    };

    const fetchEnrolledRetakesData = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/enrolments-retake/?email=${userName}`);
            setEnrolledRetakes(response.data.map(enrolment => enrolment.retake_id));
        } catch (error) {
            console.error("Ошибка при загрузке записей:", error);
        }
    };

    const handleEnroll = async (retakeId) => {
        if (!isAuthenticated) {
            alert("Для записи на пересдачу необходимо авторизоваться.");
            return;
        }

        try {
            await enrollRetake(userName, retakeId);
            alert("Вы успешно записались на пересдачу!");
            setEnrolledRetakes([...enrolledRetakes, retakeId]);
        } catch (error) {
            alert(error);
        }
    };

    const handleCancel = async (retakeId) => {
        try {
            await cancelRetake(userName, retakeId);
            alert("Запись на пересдачу отменена.");
            setEnrolledRetakes(enrolledRetakes.filter(id => id !== retakeId));
        } catch (error) {
            alert(error);
        }
    };

    return (
        <div className="retake-enroll-container">
            <div className="retakes-title">Предстоящие пересдачи</div>
            {loading && <div>Загрузка...</div>}
            {error && <div className="error-message">{error}</div>}
            <div className="grid-container">
                {retakeExams.map((retake) => (
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

export default Retakes;