import axios from "axios";
const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8080";


export const registerUser = async (name, email, password) => {
    try {
        const response = await axios.post(`${BASE_URL}/auth/registration`, {
            name,
            email,
            password,
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || "Ошибка регистрации. Попробуйте снова.");
    }
};


export const loginUser = async (email, password) => {
    try {
        const response = await axios.post(`${BASE_URL}/auth/authorization`, {
            email,
            password,
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || "Ошибка авторизации. Попробуйте снова.");
    }
};


export const fetchExams = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/exams/`);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось загрузить экзамены. Попробуйте снова.");
    }
};

export const enrollExam = async (email, examId) => {
    try {
        const data = {
            email,
            exam_id: Number(examId),
            type: "Экзамен",
            date: new Date().toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\./g, '-'), // Форматируем дату в "dd-MM-yyyy"
        };


        const response = await axios.post(`${BASE_URL}/enrolments-exams/`, data);
        return response.data;
    } catch (error) {
        console.error("Ошибка при записи на экзамен:", error.response?.data || error.message);
        throw new Error("Не удалось записаться на экзамен. Попробуйте снова.");
    }
};

export const cancelExam = async (email, examId) => {
    try {
        const response = await axios.delete(`${BASE_URL}/enrolments-exams/?email=${email}&exam_id=${examId}`);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось отменить запись на экзамен. Попробуйте снова.");
    }
};

export const fetchRetakes = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/retakes/`);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось загрузить пересдачи. Попробуйте снова.");
    }
};

export const enrollRetake = async (email, retakeId) => {
    try {
        const response = await axios.post(`${BASE_URL}/enrolments-retake/`, {
            email: email,
            retake_id: retakeId,
            type: "Пересдача",
            date: new Date().toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\./g, '-'), // Форматируем дату в "dd-MM-yyyy"
        });
        console.log(response);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось записаться на пересдачу. Попробуйте снова.");
    }
};

export const cancelRetake = async (email, retakeId) => {
    try {
        const response = await axios.delete(`${BASE_URL}/enrolments-retake/?email=${email}&retake_id=${retakeId}`);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось отменить запись на пересдачу. Попробуйте снова.");
    }
};

export const fetchEnrolledExams = async (email) => {
    try {
        const response = await axios.get(`${BASE_URL}/enrolments-exams/?email=${email}`);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось загрузить записи на экзамены. Попробуйте снова.");
    }
};

export const fetchEnrolledRetakes = async (email) => {
    try {
        const response = await axios.get(`${BASE_URL}/enrolments-retake/?email=${email}`);
        return response.data;
    } catch (error) {
        throw new Error("Не удалось загрузить записи на пересдачи. Попробуйте снова.");
    }
};