import React, { useState, useEffect, useRef } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import { profileSchema } from '../../utils/validations';
import api from '../../services/api';
import ImageUpload from './ImageUpload';
import ProjectTagsInput from './ProjectTagsInput';
import './ProfileForm.css';

const ProfileForm = () => {
  const [profile, setProfile] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [editMode, setEditMode] = useState(() => localStorage.getItem('editMode') === 'true');
  const [statusMessage, setStatusMessage] = useState(null);
  const formikRef = useRef(); //сброс формы

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/profiles/me');
        setProfile(response.data);
        setProjects(response.data.projects || []);
      } catch (error) {
        setStatusMessage('Ошибка загрузки профиля');
        console.error(error);
      }
    };
    fetchProfile();
  }, []);

  const handleEditClick = () => {
    localStorage.setItem('editMode', 'true');
    setEditMode(true);
  };

  const handleCancel = () => {
    localStorage.removeItem('editMode');
    setEditMode(false);
    setSelectedFile(null);
    setPreview(null);
    formikRef.current?.resetForm(); // сбрасываем форму до актуальной
  };

  const onSubmit = async (values, { setSubmitting }) => {
    try {
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        await api.post('/profiles/me/photo', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      const payload = { ...values, projects };
      const response = await api.put('/profiles/me', payload);
      setProfile(response.data);
      setProjects(response.data.projects || []);
      localStorage.removeItem('editMode');
      setEditMode(false);
      setSelectedFile(null);
      setPreview(null);
      setStatusMessage('Профиль обновлён');
    } catch (error) {
      console.error(error);
      setStatusMessage('Ошибка при обновлении профиля');
    } finally {
      setSubmitting(false);
    }
  };

  if (!profile) return <div className="loading">Загрузка профиля...</div>;

  const fullName = [profile.last_name, profile.first_name, profile.middle_name]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="profile-form card">
      <div className="profile-header">
        {!editMode && (
          <div className="edit-icon" title="Редактировать профиль" onClick={handleEditClick}>
            ✏️
          </div>
        )}
      </div>

      {(preview || profile.photo_thumb) && (
        <img
          className="avatar-large"
          src={preview || `http://localhost:8000/uploads/${profile.photo_thumb}`}
          alt="Фото профиля"
        />
      )}

      {!editMode && fullName && <h2 className="full-name">{fullName}</h2>}

      {editMode && (
        <ImageUpload
          onFileSelect={(file) => {
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
          }}
        />
      )}

      <Formik
        innerRef={formikRef}
        initialValues={profile}
        validationSchema={profileSchema}
        onSubmit={onSubmit}
        enableReinitialize
      >
        {({ isSubmitting }) => (
          <Form>
            {editMode && (
              <>
                {renderField('Имя', 'first_name')}
                {renderField('Фамилия', 'last_name')}
                {renderField('Отчество', 'middle_name')}
              </>
            )}

            {renderSmartField('Телефон', 'phone', profile.phone, editMode)}
            {renderSmartField('Email', 'email', profile.email, editMode)}
            {renderSmartField('Департамент', 'department', profile.department, editMode)}
            {renderSmartField('Рабочие часы', 'working_hours', profile.working_hours, editMode)}
            {renderSmartField('Доступность', 'availability', profile.availability, editMode)}
            {renderSmartField('Telegram', 'telegram_link', profile.telegram_link, editMode)}
            {renderSmartField('VK', 'vk_link', profile.vk_link, editMode)}
            {renderSmartField('Skype', 'skype_link', profile.skype_link, editMode)}
            {renderSmartField('WhatsApp', 'whatsapp_link', profile.whatsapp_link, editMode)}

            <div className="row-field">
              <label className="row-label">Проекты:</label>
              {editMode ? (
                <div className="row-input">
                  <ProjectTagsInput tags={projects} setTags={setProjects} />
                </div>
              ) : projects.length > 0 ? (
                <div className="row-value pill-inline">
                  {projects.map((proj, idx) => (
                    <span key={idx} className="mini-pill">{proj}</span>
                  ))}
                </div>
              ) : null}
            </div>

            {editMode && (
              <div className="btn-group">
                <button type="submit" disabled={isSubmitting}>Сохранить</button>
                <button type="button" className="secondary" onClick={handleCancel}>Отменить</button>
              </div>
            )}
          </Form>
        )}
      </Formik>

      {statusMessage && <div className="status-message">{statusMessage}</div>}
    </div>
  );
};

const renderField = (label, name) => (
  <div className="row-field">
    <label className="row-label">{label}:</label>
    <div className="row-input">
      <Field name={name} />
      <ErrorMessage name={name} component="div" className="error" />
    </div>
  </div>
);

const renderSmartField = (label, name, value, editMode) => {
  if (!editMode && !value) return null;

  return (
    <div className="row-field">
      <label className="row-label">{label}:</label>
      {editMode ? (
        <div className="row-input">
          <Field name={name} />
          <ErrorMessage name={name} component="div" className="error" />
        </div>
      ) : (
        <div className="row-value">{value}</div>
      )}
    </div>
  );
};

export default ProfileForm;