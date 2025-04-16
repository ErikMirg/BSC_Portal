from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.base import AppException
import logging
import traceback

logger = logging.getLogger("handlers")

async def exception_handler(_request: Request, _exc: AppException):
    logger.error(f"Обработанное исключение: {_exc.message}")
    return JSONResponse(
        status_code=_exc.status_code,
        content={"detail": _exc.message},
    )

async def global_exception_handler(_request: Request, _exc: Exception):
    error_trace = traceback.format_exc()
    logger.error(f"Необработанное исключение:\n{error_trace}")
    if any(keyword in error_trace.lower() for keyword in ["database", "cannot connect", "fatal", "critical"]):
        logger.critical("Сервер упал, требуется немедленное вмешательство!")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Попробуйте позже."},
    )