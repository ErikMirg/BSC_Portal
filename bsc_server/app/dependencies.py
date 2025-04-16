from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.crud.user import crud_user
from app.database import get_db
from app.models import User
import logging

logger = logging.getLogger("dependencies")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        login: str = payload.get("sub")
        if login is None:
            logger.warning("JWT токен не содержит логина (sub)")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"Ошибка JWT-декодирования: {e}")
        raise credentials_exception

    user = await crud_user.get_by_login(db, login=login)
    if user is None:
        logger.warning(f"Пользователь с логином '{login}' не найден")
        raise credentials_exception
    logger.info(f"Пользователь '{login}' успешно аутентифицирован")
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        logger.warning(f"Пользователь '{current_user.login}': попытка доступа к админ-функции")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    logger.info(f"Администратор '{current_user.login}' подтверждён")
    return current_user
