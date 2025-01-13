import React from "react";
import { useLocation } from "react-router-dom";
import Header from "../Header/Header";
import Footer from "../Footer/Footer";

const Layout = ({ children }) => {
    const location = useLocation();

    // Скрываем Header и Footer на странице авторизации
    const isAuthPage = location.pathname === "/" || location.pathname === "/auth";

    return (
        <div>
            {!isAuthPage && <Header />}
            <main>{children}</main>
            {!isAuthPage && <Footer />}
        </div>
    );
};

export default Layout;