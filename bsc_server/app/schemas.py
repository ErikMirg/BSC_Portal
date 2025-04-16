import re
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator, ConfigDict
from typing import Optional, List

VK_REGEX = r"^https://(www\.)?vk\.com/[A-Za-z0-9_.-]{3,30}$"
TELEGRAM_REGEX = r"^https://(www\.)?(t\.me|telegram\.me)/[A-Za-z0-9_-]{5,32}$"
SKYPE_REGEX = r"^skype:[A-Za-z0-9_.-]{3,32}(\?call)?$"
WHATSAPP_REGEX = r"^https://wa\.me/\d{10,15}$"

def validate_social_link_generic(value: str, pattern: str, platform_name: str) -> str:
    if not re.fullmatch(pattern, value):
        raise ValueError(f"Неверный формат ссылки для {platform_name}")
    return value

class Token(BaseModel):
    access_token: str
    token_type: str
    requires_password_change: bool

class TokenData(BaseModel):
    login: Optional[str] = None

class UserBase(BaseModel):
    login: str

    @classmethod
    @field_validator("login", mode="before")
    def validate_login(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3 or len(value) > 35:
            raise ValueError("Логин должен содержать от 3 до 35 символов")
        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            raise ValueError("Логин может содержать только латинские буквы, цифры и символ подчеркивания")
        return value

class UserCreate(UserBase):
    password: str
    role: str = "user"

    @classmethod
    @field_validator("password", mode="before")
    def validate_password(cls, password: str) -> str:
        if not password:
            raise ValueError("Пароль не может быть пустым")
        if len(password) < 8 or len(password) > 64:
            raise ValueError("Пароль должен содержать от 8 до 64 символов")
        if not any(c.isupper() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.islower() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not any(c.isdigit() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return password

    @classmethod
    @field_validator("role", mode="before")
    def validate_role(cls, value: str) -> str:
        allowed = {"admin", "user"}
        if value not in allowed:
            raise ValueError("Роль должна быть либо 'admin', либо 'user'")
        return value

class UserUpdate(UserBase):
    new_login: Optional[str] = None
    new_password: Optional[str] = None

class UserFirstLoginUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    old_login: str
    new_login: Optional[str] = None
    old_password: str
    new_password: Optional[str] = None
    confirm_new_password: Optional[str] = None

    @classmethod
    @field_validator("new_password", mode="before")
    def validate_password_complexity(cls, password: str) -> str:
        if not password:
            raise ValueError("Пароль не может быть пустым")
        if len(password) < 8 or len(password) > 64:
            raise ValueError("Пароль должен содержать от 8 до 64 символов")
        if not any(c.isdigit() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(c.isupper() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.islower() for c in password):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return password

    @classmethod
    @field_validator("confirm_new_password", mode="before")
    def passwords_match(cls, confirm_new_password: str, values) -> str:
        new_password = values.get("new_password")
        if new_password and confirm_new_password != new_password:
            raise ValueError("Пароли не совпадают")
        return confirm_new_password

    @classmethod
    @field_validator("new_password", mode="before")
    def password_must_differ_from_old(cls, new_password: str, values) -> str:
        old_password = values.get("old_password")
        if old_password and new_password == old_password:
            raise ValueError("Новый пароль не должен совпадать со старым")
        return new_password

### Схемы для профиля сотрудника

class EmployeeProfileCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    email: EmailStr
    department: str
    working_hours: Optional[str] = None  # Формат: чч:мм-чч:мм
    vk_link: Optional[HttpUrl] = None
    telegram_link: Optional[HttpUrl] = None
    skype_link: Optional[HttpUrl] = None
    whatsapp_link: Optional[HttpUrl] = None
    availability: Optional[str] = None

    @classmethod
    @field_validator('first_name', mode="before")
    def validate_first_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2 or len(value) > 35:
            raise ValueError("Имя должно содержать от 2 до 35 символов")
        if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-]+", value):
            raise ValueError("Имя содержит недопустимые символы (допустимы только буквы и дефис)")
        return value

    @classmethod
    @field_validator('last_name', mode="before")
    def validate_last_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2 or len(value) > 35:
            raise ValueError("Фамилия должна содержать от 2 до 35 символов")
        if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-]+", value):
            raise ValueError("Фамилия содержит недопустимые символы (допустимы только буквы и дефис)")
        return value

    @classmethod
    @field_validator('middle_name', mode="before")
    def validate_middle_name(cls, value: Optional[str]) -> Optional[str]:
        if value:
            value = value.strip()
            if len(value) > 35:
                raise ValueError("Отчество не должно превышать 35 символов")
            if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-]+", value):
                raise ValueError("Отчество содержит недопустимые символы (допустимы только буквы и дефис)")
        return value

    @classmethod
    @field_validator('phone', mode="before")
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r'^\+?[1-9][0-9]{7,14}$', value):
            raise ValueError("Неверный формат телефона")
        return value

    @classmethod
    @field_validator('department', mode="before")
    def validate_department(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Департамент обязателен для заполнения")
        if len(value) > 50:
            raise ValueError("Название департамента не должно превышать 30 символов")
        return value

    @classmethod
    @field_validator('working_hours', mode="before")
    def validate_working_hours(cls, value: Optional[str]) -> Optional[str]:
        if value and not re.fullmatch(r'\d{2}:\d{2}-\d{2}:\d{2}', value):
            raise ValueError("Рабочие часы должны быть в формате чч:мм-чч:мм")
        return value

    @classmethod
    @field_validator('vk_link', mode="before")
    def validate_vk_link(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_social_link_generic(value, VK_REGEX, "ВКонтакте")
        return value

    @classmethod
    @field_validator('telegram_link', mode="before")
    def validate_telegram_link(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_social_link_generic(value, TELEGRAM_REGEX, "Telegram")
        return value

    @classmethod
    @field_validator('skype_link', mode="before")
    def validate_skype_link(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_social_link_generic(value, SKYPE_REGEX, "Skype")
        return value

    @classmethod
    @field_validator('whatsapp_link', mode="before")
    def validate_whatsapp_link(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_social_link_generic(value, WHATSAPP_REGEX, "WhatsApp")
        return value

class EmployeeProfileUpdate(EmployeeProfileCreate):
    photo: Optional[str] = None
    projects: Optional[List[str]] = None

class EmployeeProfileOut(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    department: str
    phone: str
    email: str
    working_hours: Optional[str] = None
    availability: Optional[str] = None
    vk_link: Optional[HttpUrl] = None
    telegram_link: Optional[HttpUrl] = None
    skype_link: Optional[HttpUrl] = None
    whatsapp_link: Optional[HttpUrl] = None
    photo: Optional[str] = None
    photo_thumb: Optional[str] = None
    projects: Optional[List[str]] = None

    class Config:
        from_attributes = True