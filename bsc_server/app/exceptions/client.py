from .base import AppException

class BadRequest(AppException):
    def __init__(self, message="Некорректный запрос"):
        super().__init__(message, status_code=400)

class Unauthorized(AppException):
    def __init__(self, message="Требуется авторизация"):
        super().__init__(message, status_code=401)

class Forbidden(AppException):
    def __init__(self, message="Нет прав для выполнения действия"):
        super().__init__(message, status_code=403)

class NotFound(AppException):
    def __init__(self, message="Запрашиваемый ресурс не найден"):
        super().__init__(message, status_code=404)

class Conflict(AppException):
    def __init__(self, message="Конфликт данных"):
        super().__init__(message, status_code=409)