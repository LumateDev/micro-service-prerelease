import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        const savedAuth = localStorage.getItem("isAuthenticated");
        return savedAuth === "true";
    });

    const [userName, setUserName] = useState(() => {
        return localStorage.getItem("userName") || "";
    });

    const [userEmail, setUserEmail] = useState(() => {
        return localStorage.getItem("userEmail") || "";
    });

    useEffect(() => {
        localStorage.setItem("isAuthenticated", isAuthenticated);
        localStorage.setItem("userName", userName);
        localStorage.setItem("userEmail", userEmail);
    }, [isAuthenticated, userName, userEmail]);

    const logout = () => {
        setIsAuthenticated(false);
        setUserName("");
        setUserEmail("");
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, userName, setUserName, userEmail, setUserEmail, logout }}>
            {children}
        </AuthContext.Provider>
    );
};