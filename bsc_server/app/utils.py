import asyncio
import io
import os
import uuid
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException
from PIL import Image
import logging

logger = logging.getLogger("utils")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 15 * 1024 * 1024
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".heic", ".heif", ".raw"}


async def save_image_and_thumbnail(file: UploadFile, thumbnail_size=(400, 400)) -> tuple[str, str]:
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        logger.warning(f"Файл '{file.filename}' превышает допустимый размер")
        raise HTTPException(status_code=413, detail="Размер файла превышает 15 МБ.")

    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        logger.warning(f"Файл '{file.filename}': неподдерживаемый формат {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла: {ext}. Допустимые форматы: {allowed}"
        )

    try:
        image = await asyncio.to_thread(Image.open, io.BytesIO(contents))
        logger.info(f"Файл '{file.filename}' успешно открыт как изображение")
    except Exception as e:
        logger.error(f"Ошибка открытия изображения файла '{file.filename}': {e}")
        raise HTTPException(status_code=400, detail="Не удалось открыть файл как изображение.")

    image = await asyncio.to_thread(image.convert, "RGB")
    unique_id = uuid.uuid4().hex
    main_filename = f"{unique_id}.jpg"
    thumb_filename = f"{unique_id}_thumb.jpg"

    main_path = UPLOAD_DIR / main_filename
    thumb_path = UPLOAD_DIR / thumb_filename

    async def save_image(image_obj: Image.Image, path: Path):
        buf = io.BytesIO()
        await asyncio.to_thread(image_obj.save, buf, format="JPEG")
        data = buf.getvalue()
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)

    try:
        await save_image(image, main_path)
        logger.info(f"Основное изображение сохранено: {main_filename}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении изображения '{main_filename}': {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении основного изображения.")

    try:
        thumbnail_image = await asyncio.to_thread(image.copy)
        await asyncio.to_thread(thumbnail_image.thumbnail, thumbnail_size)
        await save_image(thumbnail_image, thumb_path)
        logger.info(f"Миниатюра успешно создана: {thumb_filename}")
    except Exception as e:
        logger.error(f"Ошибка при создании миниатюры '{thumb_filename}': {e}")
        raise HTTPException(status_code=500, detail="Ошибка при генерации миниатюры.")

    return main_filename, thumb_filename
