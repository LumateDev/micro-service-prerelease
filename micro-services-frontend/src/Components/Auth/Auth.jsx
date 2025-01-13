import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { SHA256 } from "crypto-js";
import { AuthContext } from "../../Context/AuthContext";
import "./auth.css";

import user_icon from "../Assets/person.png";
import email_icon from "../Assets/email.png";
import password_icon from "../Assets/password.png";

const Auth = () => {
  const [action, setAction] = useState("Регистрация");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { setIsAuthenticated, setUserName } = useContext(AuthContext);

  const handleRegistration = async () => {
    if (action === "Регистрация") {
      try {
        const hashedPassword = SHA256(password).toString();
        const response = await axios.post(
          "http://localhost:8000/registration",
          {
            email: email,
            password: hashedPassword,
          }
        );

        if (response.status === 200) {
          alert(response.data.message);
          setIsAuthenticated(true);
          setUserName(name);
          navigate("/home");
        } else if (response.status === 202) {
          alert(response.data.message);
        }
      } catch (error) {
        console.error("Ошибка регистрации:", error);
        alert("Ошибка регистрации. Попробуйте снова.");
      }
    } else {
      setAction("Регистрация");
    }
  };

  const handleLogin = async () => {
    if (action === "Авторизация") {
      try {
        const hashedPassword = SHA256(password).toString();
        const response = await axios.post(
          "http://localhost:8000/authorization",
          {
            email: email,
            password: hashedPassword,
          }
        );

        if (response.status === 200) {
          alert(response.data.message);
          setIsAuthenticated(true);
          setUserName(response.data.userName || "Пользователь");
          navigate("/home");
        } else if (response.status === 202) {
          alert(response.data.message);
        }
      } catch (error) {
        console.error("Ошибка авторизации:", error);
        alert("Ошибка авторизации. Попробуйте снова.");
      }
    } else {
      setAction("Авторизация");
    }
  };

  return (
    <div className="container">
      <div className="auth-header">
        <h1 className="text">
          Кто не зарегал аккаунт, тот не сдаст экзамен по микросервисам
        </h1>
        <div className="text">{action}</div>
        <div className="underline"></div>
      </div>
      <div className="inputs">
        {action === "Авторизация" ? null : (
          <div className="input">
            <img src={user_icon} alt="" />
            <input
              type="text"
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
        )}

        <div className="input">
          <img src={email_icon} alt="" />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="input">
          <img src={password_icon} alt="" />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
      </div>
      {action === "Регистрация" ? null : (
        <div className="forgot-password">
          Забыли пароль? <span>Просто кликните здесь!</span>
        </div>
      )}
      <div className="submit-container">
        <div
          className={action === "Регистрация" ? "submit gray" : "submit"}
          onClick={handleRegistration}
        >
          Зарегистрироваться
        </div>
        <div
          className={action === "Авторизация" ? "submit gray" : "submit"}
          onClick={handleLogin}
        >
          Войти
        </div>
      </div>
    </div>
  );
};

export default Auth;
