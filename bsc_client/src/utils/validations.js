import * as Yup from 'yup';

export const loginSchema = Yup.object().shape({
  login: Yup.string()
    .required('Введите логин'),

  password: Yup.string()
    .required('Введите пароль')
});

export const profileSchema = Yup.object().shape({
  first_name: Yup.string()
    .trim()
    .min(2, 'Имя должно содержать минимум 2 символа')
    .max(35, 'Имя не должно превышать 35 символов')
    .matches(/^[A-Za-zА-Яа-яЁё\-]+$/, 'Имя содержит недопустимые символы')
    .required('Обязательное поле'),

  last_name: Yup.string()
    .trim()
    .min(2, 'Фамилия должна содержать минимум 2 символа')
    .max(35, 'Фамилия не должна превышать 35 символов')
    .matches(/^[A-Za-zА-Яа-яЁё\-]+$/, 'Фамилия содержит недопустимые символы')
    .required('Обязательное поле'),

  middle_name: Yup.string()
    .trim()
    .max(35, 'Отчество не должно превышать 35 символов')
    .matches(/^[A-Za-zА-Яа-яЁё\-]*$/, 'Отчество содержит недопустимые символы')
    .nullable(),

  phone: Yup.string()
    .trim()
    .matches(/^\+?[1-9][0-9]{7,14}$/, 'Неверный формат телефона')
    .required('Обязательное поле'),

  email: Yup.string()
    .email('Неверный формат email')
    .required('Обязательное поле'),

  department: Yup.string()
    .trim()
    .max(50, 'Название департамента не должно превышать 50 символов')
    .required('Департамент обязателен'),

  working_hours: Yup.string()
    .nullable()
    .matches(/^\d{2}:\d{2}-\d{2}:\d{2}$/, 'Формат: чч:мм-чч:мм'),

  availability: Yup.string().nullable(),

  vk_link: Yup.string()
    .url('Неверная ссылка на ВКонтакте')
    .nullable(),

  telegram_link: Yup.string()
    .url('Неверная ссылка на Telegram')
    .nullable(),

  skype_link: Yup.string()
    .url('Неверная ссылка на Skype')
    .nullable(),

  whatsapp_link: Yup.string()
    .url('Неверная ссылка на WhatsApp')
    .nullable(),
});
