# apps/catalog/services/photo.py
"""Сервис обработки и загрузки фото в VK Cloud Object Storage.

Паттерн Service Layer: модель не знает про S3/Pillow, форма вызывает сервис.
"""
import logging
from io import BytesIO
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from PIL import Image

logger = logging.getLogger("avito_export")


class PhotoService:
    """Оптимизация + загрузка фото в S3 (VK Cloud)."""

    MAX_SIZE = (1920, 1080)
    JPEG_QUALITY = 85

    @classmethod
    def optimize(cls, file_bytes: bytes) -> bytes:
        """Ресайз + сжатие JPEG. Возвращает bytes."""
        img = Image.open(BytesIO(file_bytes))

        # Убираем альфа-канал (Авито не любит PNG с прозрачностью)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Ресайз с сохранением пропорций
        img.thumbnail(cls.MAX_SIZE, Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG", quality=cls.JPEG_QUALITY, optimize=True)
        return output.getvalue()

    @classmethod
    def _get_client(cls):
        """Boto3-клиент для VK Cloud (path-style, endpoint_url)."""
        return boto3.client(
            "s3",
            endpoint_url=settings.VK_S3_ENDPOINT,
            aws_access_key_id=settings.VK_S3_ACCESS_KEY,
            aws_secret_access_key=settings.VK_S3_SECRET_KEY,
            region_name=settings.VK_S3_REGION,
            config=Config(s3={"addressing_style": "virtual"}),
        )

    @classmethod
    def upload(cls, file_bytes: bytes, object_key: str) -> str:
        logger.info("s3_upload_start key=%s size=%d bucket=%s",
                    object_key, len(file_bytes), settings.VK_S3_BUCKET)
        client = cls._get_client()
        client.put_object(
            Bucket=settings.VK_S3_BUCKET,
            Key=object_key,
            Body=file_bytes,
            ACL="public-read",
            ContentType="image/jpeg",
        )
        url = f"{settings.VK_S3_PUBLIC_URL}/{object_key}"
        logger.info("s3_upload_ok key=%s url=%s", object_key, url)
        return url

    @classmethod
    def process_and_upload(cls, file_bytes: bytes, prefix: str = "products") -> str:
        logger.info("photo_process_start size=%d", len(file_bytes))
        optimized = cls.optimize(file_bytes)
        logger.info("photo_optimized size=%d", len(optimized))
        key = f"{prefix}/{uuid4().hex}.jpg"
        try:
            url = cls.upload(optimized, key)
            logger.info("photo_uploaded key=%s url=%s", key, url)
            return url
        except (BotoCoreError, ClientError) as e:
            logger.error("photo_upload_failed key=%s error=%s", key, e, exc_info=True)
            raise