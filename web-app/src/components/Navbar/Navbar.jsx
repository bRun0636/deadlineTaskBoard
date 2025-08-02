// src/components/Navbar/Navbar.jsx

import React from "react";
import "./Navbar.css";

const Navbar = ({ toggleTheme, theme, isClosed, toggleNavbar }) => {
  return (
    <div className={`navbar ${theme} ${isClosed ? "closed" : ""}`}>
      <button className="toggle-btn" onClick={toggleNavbar}>
        {isClosed ? "☰" : "✕"}
      </button>

      {!isClosed && (
        <div className="navbar-content">
          <h3>Навигация</h3>
          <ul>
            <li>Профиль</li>
            <li>Задачи</li>
            <li>Доски</li>
            <li>Статистика</li>
          </ul>

          <button className="theme-btn" onClick={toggleTheme}>
            Сменить тему
          </button>
        </div>
      )}
    </div>
  );
};

export default Navbar;
