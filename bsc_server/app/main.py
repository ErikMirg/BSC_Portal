from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import get_db, init_db
from app.models import User
from app.routers import auth, users, profiles, security
from app.crud.user import crud_user
from app.security import get_password_hash
from app.exceptions.handlers import exception_handler, global_exception_handler
from app.exceptions.base import AppException
from logging_config import setup_logging
from fastapi.middleware.cors import CORSMiddleware
from app.crud.profile import crud_profile
from app.schemas import EmployeeProfileCreate
import logging

setup_logging()
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await create_default_admin()
    yield

async def create_default_admin():
    async for db in get_db():
        try:
            admin = await crud_user.get_by_login(db, "admin")
            if not admin:
                hashed_password = get_password_hash("Admin123!")
                new_admin = User(
                    login="admin",
                    hashed_password=hashed_password,
                    role="admin",
                    created_by=None,
                    is_initial_password=True
                )
                db.add(new_admin)
                await db.commit()
                await db.refresh(new_admin)
                logger.info("Администратор успешно создан. Действие: создание администратора.")

                profile_data = EmployeeProfileCreate(
                    first_name="Админ",
                    last_name="Системный",
                    phone="+79999999999",
                    email="admin@example.com",
                    department="IT",
                    working_hours="09:00-18:00",
                    availability="Всегда на связи"
                )
                await crud_profile.create_profile(db, profile_data, new_admin.id)
                logger.info("Профиль администратора успешно создан.")
        except Exception as e:
            logger.error(f"Ошибка создания администратора: {e}")
            logger.critical("Сбой при создании администратора! Возможно, приложение не сможет функционировать без него.")
        break

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешённый источник, можно указать * - для всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(security.router)

@app.get("/")
async def read_root():
    logger.info("Открыта главная страница.")
    return {"message": "Дом... Милый дом! Ты ведь помнишь, что BSC твоя вторая семья?)"}

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_exception_handler(AppException, exception_handler)
app.add_exception_handler(Exception, global_exception_handler)