import './style/main.css';

import React, { useContext } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthContext } from "./Context/AuthContext";
import AuthPage from "./Pages/AuthPage";
import HomePage from "./Pages/HomePage";
import CourseEnrollPage from "./Pages/CourseEnrollPage";
import RetakeEnrollPage from "./Pages/RetakeEnrollPage";
import LecturesPage from "./Pages/LecturesPage";
import Layout from "./Components/Layout/Layout";

function App() {
    const { isAuthenticated } = useContext(AuthContext);

    return (
        <Layout>
            <Routes>
                <Route
                    path="/"
                    element={isAuthenticated ? <Navigate to="/home" /> : <AuthPage />}
                />
                <Route
                    path="/auth"
                    element={isAuthenticated ? <Navigate to="/home" /> : <AuthPage />}
                />
                <Route
                    path="/home"
                    element={isAuthenticated ? <HomePage /> : <Navigate to="/auth" />}
                />
                <Route
                    path="/course-enroll"
                    element={isAuthenticated ? <CourseEnrollPage /> : <Navigate to="/auth" />}
                />
                <Route
                    path="/retake-enroll"
                    element={isAuthenticated ? <RetakeEnrollPage /> : <Navigate to="/auth" />}
                />
                <Route
                    path="/lectures"
                    element={isAuthenticated ? <LecturesPage /> : <Navigate to="/auth" />}
                />
            </Routes>
        </Layout>
    );
}

export default App;