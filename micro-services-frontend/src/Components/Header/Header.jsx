import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../../Context/AuthContext";
import "./header.css";

const Header = () => {
    const { userName, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/auth");
    };

    return (
        <header className="header">
            <div className="logo">
                <Link to="/home">MicroServices App</Link>
            </div>
            <nav className="nav">
                <ul>
                    <li>
                        <Link to="/сourse-enroll">Запись на экзамен</Link>
                    </li>
                    <li>
                        <Link to="/retake-enroll">Запись на пересдачу</Link>
                    </li>
                    <li>
                        <Link to="/lectures">Лекции</Link>
                    </li>
                </ul>
            </nav>
            {userName && (
                <div className="user-info">
                    <li>
                        <Link to="/home"><span className="username">{userName}</span></Link>
                    </li>

                    <button className="logout-button" onClick={handleLogout}>
                        Выйти
                    </button>
                </div>
            )}
        </header>
    );
};

export default Header;