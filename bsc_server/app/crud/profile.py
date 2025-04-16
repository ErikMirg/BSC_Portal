import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import EmployeeProfile
from app.schemas import EmployeeProfileCreate, EmployeeProfileUpdate
from app.cache import get_cache, set_cache
from app.exceptions.client import NotFound
from app.exceptions.server import DatabaseError
from pydantic import HttpUrl
import logging

logger = logging.getLogger("crud")

UPLOAD_DIR = Path("uploads")

class CRUDProfile:
    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int):
        try:
            logger.info(f"Получение профиля для user_id {user_id}")
            result = await db.execute(select(EmployeeProfile).where(EmployeeProfile.user_id == user_id))
            profile = result.scalar_one_or_none()
            if not profile:
                logger.warning(f"Профиль для user_id {user_id} не найден")
                raise NotFound(f"Профиль для user_id {user_id} не найден")
            return profile
        except Exception as e:
            logger.error(f"Ошибка получения профиля для user_id {user_id}: {e}")
            await db.rollback()
            raise DatabaseError(f"Ошибка получения профиля: {e}")

    @staticmethod
    async def create_profile(db: AsyncSession, profile: EmployeeProfileCreate, user_id: int):
        try:
            data = profile.model_dump()
            db_profile = EmployeeProfile(**data, user_id=user_id)
            db.add(db_profile)
            await db.commit()
            await db.refresh(db_profile)
            logger.info(f"Профиль для user_id {user_id} успешно создан")
            return db_profile
        except Exception as e:
            logger.error(f"Ошибка создания профиля для user_id {user_id}: {e}")
            await db.rollback()
            raise DatabaseError(f"Ошибка создания профиля: {e}")

    @staticmethod
    async def update_profile(db: AsyncSession, profile: EmployeeProfile, updates: EmployeeProfileUpdate) -> EmployeeProfile:
        try:
            update_data = updates.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if isinstance(value, HttpUrl):
                    update_data[field] = str(value)
                setattr(profile, field, update_data[field])
            logger.info(f"Обновление профиля id {profile.id} с данными: {update_data}")
            for field, value in update_data.items():
                setattr(profile, field, value)
            await db.commit()
            await db.refresh(profile)
            logger.info(f"Профиль id {profile.id} успешно обновлен")
            return profile
        except Exception as e:
            logger.error(f"Ошибка обновления профиля id {profile.id}: {e}")
            await db.rollback()
            raise DatabaseError(f"Ошибка обновления профиля: {e}")

    @staticmethod
    async def delete_profile(db: AsyncSession, user_id: int) -> None:
        result = await db.execute(select(EmployeeProfile).where(EmployeeProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if profile:
            if profile.photo:
                photo_path = UPLOAD_DIR / profile.photo
                if photo_path.exists():
                    try:
                        os.remove(photo_path)
                        logger.info(f"Основное изображение профиля {profile.id} удалено")
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла {photo_path}: {e}")
            if profile.photo_thumb:
                thumb_path = UPLOAD_DIR / profile.photo_thumb
                if thumb_path.exists():
                    try:
                        os.remove(thumb_path)
                        logger.info(f"Миниатюра профиля {profile.id} удалена")
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла {thumb_path}: {e}")
            try:
                await db.delete(profile)
                await db.commit()
                logger.info(f"Профиль для user_id {user_id} успешно удален")
            except Exception as e:
                logger.error(f"Ошибка удаления профиля для user_id {user_id}: {e}")
                await db.rollback()
                raise DatabaseError(f"Ошибка удаления профиля: {e}")
        else:
            logger.warning(f"Профиль для user_id {user_id} не найден для удаления")
        return None

    @staticmethod
    async def search_profiles(db: AsyncSession, search_term: str):
        cache_key = f"search:{search_term.lower()}"
        cached = await get_cache(cache_key)
        if cached:
            logger.info(f"Поиск профилей для '{search_term}': результаты найдены в кэше")
            return cached
        try:
            from sqlalchemy import or_
            query = select(EmployeeProfile).where(
                or_(
                    EmployeeProfile.first_name.ilike(f"%{search_term}%"),
                    EmployeeProfile.last_name.ilike(f"%{search_term}%"),
                    EmployeeProfile.middle_name.ilike(f"%{search_term}%"),
                    EmployeeProfile.phone.ilike(f"%{search_term}%"),
                    EmployeeProfile.email.ilike(f"%{search_term}%"),
                    EmployeeProfile.department.ilike(f"%{search_term}%")
                )
            )
            result = await db.execute(query)
            results = result.scalars().all()
            serialized = [
                {
                    "id": profile.id,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "middle_name": profile.middle_name,
                    "phone": profile.phone,
                    "email": profile.email,
                    "department": profile.department
                }
                for profile in results
            ]
            await set_cache(cache_key, serialized, expire=60)
            logger.info(f"Поиск профилей для '{search_term}': найдено {len(results)} результатов")
            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске профилей для '{search_term}': {e}")
            await db.rollback()
            raise DatabaseError(f"Ошибка при поиске профилей: {e}")

    @staticmethod
    async def get_all_profiles(db: AsyncSession) -> list[EmployeeProfile]:
        try:
            logger.info("Получение всех профилей")
            result = await db.execute(select(EmployeeProfile))
            profiles = result.scalars().all()
            logger.info(f"Получено {len(profiles)} профилей")
            return profiles
        except Exception as e:
            logger.error(f"Ошибка получения всех профилей: {e}")
            await db.rollback()
            raise DatabaseError(f"Ошибка получения всех профилей: {e}")

    @staticmethod
    async def get_profile_by_id(db: AsyncSession, profile_id: int) -> EmployeeProfile:
        try:
            logger.info(f"Получение профиля по profile_id={profile_id}")
            result = await db.execute(select(EmployeeProfile).where(EmployeeProfile.id == profile_id))
            profile = result.scalar_one_or_none()
            if not profile:
                logger.warning(f"Профиль с profile_id={profile_id} не найден")
                raise NotFound(f"Профиль с id={profile_id} не найден")
            return profile
        except Exception as e:
            logger.error(f"Ошибка при получении профиля profile_id={profile_id}: {e}")
            await db.rollback()
            raise DatabaseError(f"Ошибка получения профиля: {e}")

crud_profile = CRUDProfile()