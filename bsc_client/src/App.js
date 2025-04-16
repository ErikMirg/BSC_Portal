import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginForm from './components/Auth/LoginForm';
import ProfileForm from './components/Profiles/ProfileForm';
import UserCreateForm from './components/Users/UserCreateForm';
import AllProfiles from './components/Profiles/AllProfiles';
import ProfileView from './components/Profiles/ProfileView';
import Navbar from './components/common/Navbar';
import useAuthCheck from './hooks/useAuthCheck';

const App = () => (
  <Router>
    <AppWithRouter />
  </Router>
);

const AppWithRouter = () => {
  const loading = useAuthCheck();
  const token = localStorage.getItem('token');

  if (loading) return <div style={{ textAlign: 'center', marginTop: '3rem' }}>Проверка авторизации...</div>;

  return (
    <>
      {token && <Navbar />}
      <Routes>
        <Route path="/" element={<Navigate to={token ? '/profile' : '/login'} />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/profile" element={token ? <ProfileForm /> : <Navigate to="/login" />} />
        <Route path="/create-user" element={token ? <UserCreateForm /> : <Navigate to="/login" />} />
        <Route path="/all-profiles" element={token ? <AllProfiles /> : <Navigate to="/login" />} />
        <Route path="/profile/:id" element={token ? <ProfileView /> : <Navigate to="/login" />} />
      </Routes>
    </>
  );
};

export default App;