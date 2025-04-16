from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.database import get_db
from app.schemas import Token
from app.security import create_access_token, verify_password
from app.crud.user import crud_user
from app.config import settings
import logging

logger = logging.getLogger("auth")
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Попытка входа: пользователь {form_data.username}")
    user = await crud_user.get_by_login(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа: неправильное имя пользователя или пароль для {form_data.username}")
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login},
        expires_delta=access_token_expires
    )
    logger.info(f"Успешный вход: {user.login}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_password_change": user.is_initial_password
    }
