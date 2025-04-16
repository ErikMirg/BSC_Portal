import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import './UserCreateForm.css';

const validationSchema = Yup.object().shape({
  login: Yup.string()
    .trim()
    .min(3, 'Логин должен содержать минимум 3 символа')
    .max(35, 'Логин не должен превышать 35 символов')
    .matches(/^[A-Za-z0-9_]+$/, 'Логин может содержать только латинские буквы, цифры и символ _')
    .required('Обязательное поле'),

  password: Yup.string()
    .min(8, 'Пароль должен содержать минимум 8 символов')
    .max(64, 'Пароль не должен превышать 64 символа')
    .matches(/[A-Z]+/, 'Пароль должен содержать хотя бы одну заглавную букву')
    .matches(/[a-z]+/, 'Пароль должен содержать хотя бы одну строчную букву')
    .matches(/\d+/, 'Пароль должен содержать хотя бы одну цифру')
    .matches(/[!@#$%^&*()\-_=+[\]{}\\|;:'",<.>/?`~]+/, 'Пароль должен содержать хотя бы один спецсимвол')
    .required('Обязательное поле'),

  role: Yup.string()
    .oneOf(['employee', 'admin'], 'Выберите корректную роль')
    .required('Обязательное поле'),
});

const UserCreateForm = () => {
  const navigate = useNavigate();

  const initialValues = {
    login: '',
    password: '',
    role: 'employee',
  };

  const onSubmit = async (values, { setSubmitting, setFieldError, resetForm }) => {
    try {
      await api.post('/users/', values);
      resetForm();
      alert('Пользователь создан!');
      navigate('/profile');
    } catch (error) {
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          setFieldError('login', detail);
        } else if (Array.isArray(detail)) {
          detail.forEach(err => {
            if (err.loc?.[1]) {
              setFieldError(err.loc[1], err.msg);
            }
          });
        }
      } else {
        alert('Ошибка при создании пользователя');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="create-user-form card">
      <h2 className="form-title">Создание нового пользователя</h2>

      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={onSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <div className="row-field">
              <label className="row-label">Логин:</label>
              <div className="row-input">
                <Field name="login" />
                <ErrorMessage name="login" component="div" className="error" />
              </div>
            </div>

            <div className="row-field">
              <label className="row-label">Пароль:</label>
              <div className="row-input">
                <Field type="password" name="password" />
                <ErrorMessage name="password" component="div" className="error" />
              </div>
            </div>

            <div className="row-field">
              <label className="row-label">Роль:</label>
              <div className="row-input">
                <Field as="select" name="role" className="select-field">
                  <option value="employee">Сотрудник</option>
                  <option value="admin">Администратор</option>
                </Field>
                <ErrorMessage name="role" component="div" className="error" />
              </div>
            </div>

            <div className="btn-group center">
              <button type="submit" disabled={isSubmitting}>Создать</button>
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default UserCreateForm;
