import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <h3 className="navbar-logo">BSC Corporation</h3>
      <div className="navbar-links">
        <Link to="/profile" className="navbar-link">Мой профиль 🦧</Link>
        <Link to="/create-user" className="navbar-link">Создать коллегу 🐣</Link>
        <Link to="/all-profiles" className="navbar-link">Моя семья 🐾</Link>
        <span className="navbar-link logout" onClick={handleLogout}>Выйти 🏃</span>
      </div>
    </nav>
  );
};

export default Navbar;
