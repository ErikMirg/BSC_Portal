from .base import AppException

class InternalServerError(AppException):
    def __init__(self, message="Внутренняя ошибка сервера"):
        super().__init__(message, status_code=500)

class DatabaseError(AppException):
    def __init__(self, message="Ошибка базы данных"):
        super().__init__(message, status_code=500)