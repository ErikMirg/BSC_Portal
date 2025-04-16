import React from 'react';
import { Formik, Form, Field, useFormikContext } from 'formik';
import { loginSchema } from '../../utils/validations';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

const FieldWithError = ({ name, type = 'text', label }) => {
  const { errors, touched } = useFormikContext();
  const hasError = errors[name] && touched[name];

  return (
    <div className="row-field">
      <label className="row-label">{label}:</label>
      <div className="row-input">
        <Field name={name} type={type} />
        <div className="error">{hasError ? errors[name] : '\u00A0'}</div>
      </div>
    </div>
  );
};

const LoginForm = () => {
  const navigate = useNavigate();
  const initialValues = { login: '', password: '' };

  const onSubmit = async (values, { setSubmitting, setFieldError }) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', values.login);
      formData.append('password', values.password);

      const response = await api.post('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      localStorage.setItem('token', response.data.access_token);
      navigate('/profile');
    } catch (error) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail;

      if (status === 422 || status === 401) {
        setFieldError('password', 'Неверный логин или пароль');
      } else if (typeof detail === 'string') {
        setFieldError('password', detail);
      } else {
        setFieldError('password', 'Ошибка при попытке входа');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-form card">
      <h2 className="form-title">Вход</h2>

      <Formik
        initialValues={initialValues}
        validationSchema={loginSchema}
        onSubmit={onSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <FieldWithError name="login" label="Логин" />
            <FieldWithError name="password" type="password" label="Пароль" />

            <div className="btn-group center">
              <button type="submit" disabled={isSubmitting}>
                Войти
              </button>
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default LoginForm;