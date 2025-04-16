from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.schemas import UserCreate, EmployeeProfileCreate
from app.security import get_password_hash
from app.crud.profile import crud_profile
import logging

logger = logging.getLogger("crud")

class CRUDUser:
    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> User | None:
        logger.info(f"Получение пользователя по id: {user_id}")
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_login(db: AsyncSession, login: str) -> User | None:
        logger.info(f"Получение пользователя по логину: {login}")
        result = await db.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate, created_by: int) -> User:
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                login=user.login,
                hashed_password=hashed_password,
                role=user.role,
                created_by=created_by
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            logger.info(f"Пользователь {db_user.login} успешно создан")
        except Exception as e:
            logger.error(f"Ошибка создания пользователя: {e}")
            await db.rollback()
            raise e

        profile_email = db_user.login if "@" in db_user.login else "default@example.com"
        profile_data = EmployeeProfileCreate(
            first_name="Имя по умолчанию",
            last_name="Фамилия по умолчанию",
            phone="+70000000000",
            email=profile_email,
            department="Не указан",
            working_hours="09:00-18:00",
            availability="Не указано"
        )
        try:
            await crud_profile.create_profile(db, profile_data, db_user.id)
            logger.info(f"Профиль для пользователя {db_user.login} успешно создан")
        except Exception as e:
            logger.error(f"Ошибка создания профиля для пользователя {db_user.login}: {e}")
            raise e

        return db_user

    @staticmethod
    async def update_credentials(db: AsyncSession, user: User, new_login: str | None = None,
                                 new_password: str | None = None) -> User:
        if new_login:
            user.login = new_login
        if new_password:
            user.hashed_password = get_password_hash(new_password)
            user.is_initial_password = False
        try:
            await db.commit()
            await db.refresh(user)
            logger.info(f"Учетные данные пользователя {user.login} успешно обновлены")
        except Exception as e:
            logger.error(f"Ошибка обновления учетных данных для пользователя {user.login}: {e}")
            await db.rollback()
            raise e
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            try:
                await crud_profile.delete_profile(db, user_id)
                await db.delete(user)
                await db.commit()
                logger.info(f"Пользователь {user.login} удален")
                return user
            except Exception as e:
                logger.error(f"Ошибка удаления пользователя {user.login}: {e}")
                await db.rollback()
                raise e
        logger.warning(f"Пользователь с id {user_id} не найден для удаления")
        return None

crud_user = CRUDUser()
