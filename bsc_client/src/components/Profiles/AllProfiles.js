import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './AllProfiles.css';

const AllProfiles = () => {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const handleProfileClick = (profileId) => {
  navigate(`/profile/${profileId}`);
};

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const response = await api.get('/profiles/viewProfiles');
        setProfiles(response.data);
      } catch (err) {
        setError('Не удалось загрузить список сотрудников');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiles();
  }, []);

  if (loading) return <div className="loading">Загрузка профилей...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="profiles-container">
      {profiles.map((p) => (
        <div
          className="profile-card"
          key={p.id}
          onClick={() => handleProfileClick(p.id)}
        >
          <img
            src={
              p.photo_thumb
                ? `http://localhost:8000/uploads/${p.photo_thumb}`
                : '/default-avatar.jpg'
            }
            alt="Фото"
            className="profile-photo"
          />
          <h3 className="profile-name">
            {(p.first_name === 'Имя по умолчанию' && p.last_name === 'Фамилия по умолчанию')
              ? 'Кто-то новенький 🙈'
              : [p.last_name, p.first_name, p.middle_name].filter(Boolean).join(' ')
            }
          </h3>
          <div className="profile-dept">{p.department}</div>
          <div className="profile-line">☎️ {p.phone}</div>
          <div className="profile-line">📧 {p.email}</div>
        </div>
      ))}
    </div>
  );
};

export default AllProfiles;