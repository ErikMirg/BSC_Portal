from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models, dependencies
from app.database import get_db
from app.security import verify_password
import logging

logger = logging.getLogger("security")
router = APIRouter(prefix="/security", tags=["security"])

@router.put("/credentials", response_model=schemas.UserBase)
async def update_credentials(
    credentials: schemas.UserFirstLoginUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if not verify_password(credentials.old_password, current_user.hashed_password):
        logger.warning(f"Пользователь {current_user.login}: неверный текущий пароль при попытке обновления учетных данных")
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    if credentials.new_login and credentials.new_login != current_user.login:
        existing_user = await crud.crud_user.get_by_login(db, credentials.new_login)
        if existing_user:
            logger.warning(f"Пользователь {current_user.login}: попытка смены логина на уже используемый {credentials.new_login}")
            raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    updated_user = await crud.crud_user.update_credentials(
        db=db,
        user=current_user,
        new_login=credentials.new_login,
        new_password=credentials.new_password
    )
    logger.info(f"Пользователь {current_user.login}: обновил учетные данные")
    return updated_user

@router.post("/skip-password-change", response_model=schemas.UserBase)
async def skip_password_change(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    current_user.is_initial_password = False
    await db.commit()
    logger.info(f"Пользователь {current_user.login}: пропустил смену пароля")
    return current_user
