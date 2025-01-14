import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../Context/AuthContext";
import { registerUser, loginUser } from "../../api/api";
import "./auth.css";

import user_icon from "../Assets/person.png";
import email_icon from "../Assets/email.png";
import password_icon from "../Assets/password.png";

const Auth = () => {
  const [action, setAction] = useState("Регистрация");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [nameError, setNameError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const navigate = useNavigate();
  const { setIsAuthenticated, setUserName, setUserEmail } = useContext(AuthContext);

  const validateName = (value) => {
    if (action === "Регистрация") {
      if (!value) {
        setNameError("Имя не может быть пустым");
        return false;
      } else if (value.length < 2) {
        setNameError("Имя должно содержать минимум 2 символа");
        return false;
      } else {
        setNameError("");
        return true;
      }
    }
    return true;
  };

  const validateEmail = (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) {
      setEmailError("Email не может быть пустым");
      return false;
    } else if (!emailRegex.test(value)) {
      setEmailError("Введите корректный email");
      return false;
    } else {
      setEmailError("");
      return true;
    }
  };


  const validatePassword = (value) => {
    if (!value) {
      setPasswordError("Пароль не может быть пустым");
      return false;
    } else if (value.length < 6) {
      setPasswordError("Пароль должен содержать минимум 6 символов");
      return false;
    } else {
      setPasswordError("");
      return true;
    }
  };

  const handleRegistration = async () => {
    if (action === "Регистрация") {
      setLoading(true);
      setError("");

      const isNameValid = validateName(name);
      const isEmailValid = validateEmail(email);
      const isPasswordValid = validatePassword(password);

      if (!isNameValid || !isEmailValid || !isPasswordValid) {
        setLoading(false);
        return;
      }

      try {
        await registerUser(name, email, password);
        alert("Регистрация прошла успешно!");
        setIsAuthenticated(true);
        setUserName(name);
        setUserEmail(email);
        navigate("/home");
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    } else {
      setAction("Регистрация");
    }
  };

  const handleLogin = async () => {
    if (action === "Авторизация") {
      setLoading(true);
      setError("");

      const isEmailValid = validateEmail(email);
      const isPasswordValid = validatePassword(password);

      if (!isEmailValid || !isPasswordValid) {
        setLoading(false);
        return;
      }

      try {
        const response = await loginUser(email, password);
        alert("Авторизация прошла успешно!");
        setIsAuthenticated(true);
        setUserName(response.name || "Пользователь");
        setUserEmail(email);
        navigate("/home");
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    } else {
      setAction("Авторизация");
    }
  };

  return (
      <div className="container">
        <div className="auth-header">
          <h1 className="text">Кто не зарегал аккаунт, тот не сдаст экзамен по микросервисам</h1>
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
                    onChange={(e) => {
                      setName(e.target.value);
                      validateName(e.target.value);
                    }}
                />
                {nameError && <div className="error-message">{nameError}</div>}
              </div>
          )}

          <div className="input">
            <img src={email_icon} alt="" />
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  validateEmail(e.target.value);
                }}
            />
            {emailError && <div className="error-message">{emailError}</div>}
          </div>
          <div className="input">
            <img src={password_icon} alt="" />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  validatePassword(e.target.value);
                }}
            />
            {passwordError && <div className="error-message">{passwordError}</div>}
          </div>
        </div>
        {error && <div className="error-message">{error}</div>}
        {action === "Регистрация" ? null : (
            <div className="forgot-password">
              Забыли пароль? <span>Просто кликните здесь!</span>
            </div>
        )}
        <div className="submit-container">
          <div
              className={action === "Регистрация" ? "submit gray" : "submit"}
              onClick={handleRegistration}
              disabled={loading}
          >
            {loading ? "Загрузка..." : "Зарегистрироваться"}
          </div>
          <div
              className={action === "Авторизация" ? "submit gray" : "submit"}
              onClick={handleLogin}
              disabled={loading}
          >
            {loading ? "Загрузка..." : "Войти"}
          </div>
        </div>
      </div>
  );
};

export default Auth;