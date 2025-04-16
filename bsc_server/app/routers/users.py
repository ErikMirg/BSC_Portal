from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models
from app.database import get_db
from app.dependencies import get_current_admin
import logging

logger = logging.getLogger("users")
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserBase)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    existing_user = await crud.crud_user.get_by_login(db, user.login)
    if existing_user:
        logger.warning(f"Администратор {admin.login}: попытка создать пользователя с уже зарегистрированным логином {user.login}")
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже зарегистрирован")
    new_user = await crud.crud_user.create_user(db=db, user=user, created_by=admin.id)
    logger.info(f"Администратор {admin.login}: создан пользователь {new_user.login}")
    return new_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    if admin.id == user_id:
        logger.warning(f"Администратор {admin.login}: попытка удалить самого себя")
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")
    deleted_user = await crud.crud_user.delete_user(db, user_id)
    if not deleted_user:
        logger.warning(f"Администратор {admin.login}: попытка удаления несуществующего пользователя с id {user_id}")
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    logger.info(f"Администратор {admin.login}: удален пользователь {deleted_user.login}")
    return {"message": "Пользователь и его профиль успешно удалены"}
