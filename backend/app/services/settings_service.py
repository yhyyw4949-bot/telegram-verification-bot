from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import PlatformSetting


class SettingsService:

    @staticmethod
    async def get(db: AsyncSession, key: str, default: str = None) -> Optional[str]:
        result = await db.execute(select(PlatformSetting).where(PlatformSetting.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    @staticmethod
    async def set(db: AsyncSession, key: str, value: str):
        result = await db.execute(select(PlatformSetting).where(PlatformSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            setting = PlatformSetting(key=key, value=value)
            db.add(setting)
        await db.commit()

    @staticmethod
    async def get_all(db: AsyncSession) -> dict:
        result = await db.execute(select(PlatformSetting))
        return {s.key: s.value for s in result.scalars().all()}

    @staticmethod
    async def seed_defaults(db: AsyncSession):
        defaults = {
            "min_deposit": "5",
            "min_withdrawal": "5",
            "referral_reward": "2",
            "support_username": "support_admin",
            "platform_name": "VerifPlatform",
            "maintenance_mode": "false",
        }
        for key, value in defaults.items():
            existing = await SettingsService.get(db, key)
            if existing is None:
                await SettingsService.set(db, key, value)
