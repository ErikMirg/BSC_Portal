import os
import asyncio
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user
from app.database import get_db
from app.crud import crud_profile
from app.models import User
from app.utils import save_image_and_thumbnail
from app.schemas import EmployeeProfileUpdate, EmployeeProfileOut
import logging
from app.exceptions.client import NotFound

logger = logging.getLogger("profiles")
router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=EmployeeProfileOut)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    profile = await crud_profile.get_profile(db, current_user.id)
    if not profile:
        logger.warning(f"Пользователь {current_user.login}: профиль не найден при попытке запроса")
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    logger.info(f"Пользователь {current_user.login}: получил свой профиль")
    return profile


@router.post("/me/photo")
async def upload_profile_photo(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    profile = await crud_profile.get_profile(db, current_user.id)
    if not profile:
        logger.warning(f"Пользователь {current_user.login}: попытка загрузить фото, но профиль не найден")
        raise HTTPException(status_code=404, detail="Профиль не найден.")

    if profile.photo:
        old_main_path = os.path.join("uploads", profile.photo)
        exists = await asyncio.to_thread(os.path.exists, old_main_path)
        if exists:
            try:
                await asyncio.to_thread(os.remove, old_main_path)
                logger.info(f"Удалено старое изображение для пользователя {current_user.login}")
            except Exception as e:
                logger.error(f"Ошибка удаления старого изображения у {current_user.login}: {e}")
                raise HTTPException(status_code=500, detail=f"Ошибка при удалении старого изображения: {e}")

    if profile.photo_thumb:
        old_thumb_path = os.path.join("uploads", profile.photo_thumb)
        exists = await asyncio.to_thread(os.path.exists, old_thumb_path)
        if exists:
            try:
                await asyncio.to_thread(os.remove, old_thumb_path)
                logger.info(f"Удалена старая миниатюра для пользователя {current_user.login}")
            except Exception as e:
                logger.error(f"Ошибка удаления старой миниатюры у {current_user.login}: {e}")
                raise HTTPException(status_code=500, detail=f"Ошибка при удалении старой миниатюры: {e}")

    try:
        main_filename, thumb_filename = await save_image_and_thumbnail(file)
    except HTTPException as e:
        logger.error(f"Пользователь {current_user.login}: ошибка загрузки изображения - {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Пользователь {current_user.login}: непредвиденная ошибка загрузки изображения - {e}")
        raise HTTPException(status_code=500, detail="Непредвиденная ошибка при сохранении изображения.")

    profile.photo = main_filename
    profile.photo_thumb = thumb_filename

    try:
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        logger.info(f"Пользователь {current_user.login}: успешно загружена фотография")
    except Exception as e:
        await db.rollback()
        logger.error(f"Пользователь {current_user.login}: ошибка обновления профиля после загрузки фото - {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления профиля: {e}")

    return {
        "message": "Фотография и миниатюра успешно загружены.",
        "file_url": f"/uploads/{main_filename}",
        "thumbnail_url": f"/uploads/{thumb_filename}"
    }

@router.put("/me", response_model=EmployeeProfileOut)
async def update_profile(
        profile_in: EmployeeProfileUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    profile = await crud_profile.get_profile(db, current_user.id)
    if not profile:
        logger.warning(f"Пользователь {current_user.login}: попытка обновления профиля, но профиль не найден")
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    updated_profile = await crud_profile.update_profile(db, profile, profile_in)
    logger.info(f"Пользователь {current_user.login}: обновил свой профиль")
    return updated_profile

@router.delete("/me", response_model=dict)
async def delete_profile(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    profile = await crud_profile.get_profile(db, current_user.id)
    if not profile:
        logger.warning(f"Пользователь {current_user.login}: попытка удаления профиля, но профиль не найден")
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    await crud_profile.delete_profile(db, profile.id)
    logger.info(f"Пользователь {current_user.login}: удалил свой профиль")
    return {"message": "Профиль успешно удален"}

@router.get("/viewProfiles", response_model=list[EmployeeProfileOut])
async def get_all_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        profiles = await crud_profile.get_all_profiles(db)
        logger.info(f"Пользователь {current_user.login} запросил все профили. Получено профилей: {len(profiles)}")
        return profiles
    except Exception as e:
        logger.error(f"Ошибка получения всех профилей для пользователя {current_user.login}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении всех профилей")

@router.get("/profileStranger", response_model=EmployeeProfileOut)
async def get_profile_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        profile = await crud_profile.get_profile(db, user_id)
        logger.info(f"Пользователь {current_user.login} запросил профиль пользователя user_id={user_id}")
        return profile
    except NotFound as nf:
        logger.warning(f"Пользователь {current_user.login}: профиль user_id={user_id} не найден")
        raise HTTPException(status_code=404, detail=str(nf))
    except Exception as e:
        logger.error(f"Ошибка при получении профиля user_id={user_id} пользователем {current_user.login}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении профиля")

@router.put("/profileStranger", response_model=EmployeeProfileOut)
async def update_other_profile(
    profile_id: int,
    profile_in: EmployeeProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        logger.warning(f"Пользователь {current_user.login}: попытка редактирования чужого профиля без прав администратора")
        raise HTTPException(status_code=403, detail="Нет прав на редактирование чужих профилей")
    try:
        profile = await crud_profile.get_profile_by_id(db, profile_id)
    except NotFound as nf:
        logger.warning(f"Администратор {current_user.login}: профиль profile_id={profile_id} не найден")
        raise HTTPException(status_code=404, detail=str(nf))
    except Exception as e:
        logger.error(f"Администратор {current_user.login}: ошибка при получении профиля profile_id={profile_id} — {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении профиля")
    try:
        updated_profile = await crud_profile.update_profile(db, profile, profile_in)
        logger.info(f"Администратор {current_user.login}: обновил профиль profile_id={profile_id}")
        return updated_profile
    except Exception as e:
        logger.error(f"Администратор {current_user.login}: ошибка при обновлении профиля profile_id={profile_id} — {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении профиля")