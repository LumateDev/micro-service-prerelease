import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    // Проверяем localStorage при загрузке приложения
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        const savedAuth = localStorage.getItem("isAuthenticated");
        return savedAuth === "true";
    });

    const [userName, setUserName] = useState(() => {
        return localStorage.getItem("userName") || "";
    });

    // Сохраняем состояние авторизации и имя пользователя в localStorage при изменении
    useEffect(() => {
        localStorage.setItem("isAuthenticated", isAuthenticated);
        localStorage.setItem("userName", userName);
    }, [isAuthenticated, userName]);

    const logout = () => {
        setIsAuthenticated(false);
        setUserName("");
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, userName, setUserName, logout }}>
            {children}
        </AuthContext.Provider>
    );
};