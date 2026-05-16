import secrets
import string
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.models import User, Balance, Referral, Notification
from app.core.security import get_password_hash, verify_password
from app.schemas.schemas import UserRegister


def _gen_referral_code(n=8) -> str:
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(n))


class UserService:

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram(db: AsyncSession, telegram_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_referral_code(db: AsyncSession, code: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.referral_code == code))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, data: UserRegister) -> User:
        # Generate unique referral code
        code = _gen_referral_code()
        while (await db.execute(select(User).where(User.referral_code == code))).scalar_one_or_none():
            code = _gen_referral_code()

        referred_by = None
        if data.referral_code:
            referrer = await UserService.get_by_referral_code(db, data.referral_code)
            if referrer:
                referred_by = referrer.id

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=get_password_hash(data.password) if data.password else None,
            first_name=data.first_name,
            last_name=data.last_name,
            language=data.language or "ar",
            referral_code=code,
            referred_by_id=referred_by,
        )
        db.add(user)
        await db.flush()

        # Create balance
        balance = Balance(user_id=user.id)
        db.add(balance)

        # Record referral
        if referred_by:
            from app.services.settings_service import SettingsService
            reward = float(await SettingsService.get(db, "referral_reward", "2.0"))
            referral = Referral(referrer_id=referred_by, referred_id=user.id, reward_amount=reward)
            db.add(referral)
            # Pay referrer
            await db.execute(
                update(Balance).where(Balance.user_id == referred_by)
                .values(amount=Balance.amount + reward, total_earned=Balance.total_earned + reward)
            )

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        user = await UserService.get_by_username(db, username)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def sync_telegram_user(db: AsyncSession, telegram_id: int, telegram_username: str,
                                  first_name: str, last_name: str = None,
                                  referral_code: str = None) -> User:
        user = await UserService.get_by_telegram(db, telegram_id)
        if user:
            user.telegram_username = telegram_username
            user.first_name = first_name
            await db.commit()
            await db.refresh(user)
            return user

        # Create new user from Telegram
        code = _gen_referral_code()
        referred_by = None
        if referral_code:
            referrer = await UserService.get_by_referral_code(db, referral_code)
            if referrer:
                referred_by = referrer.id

        user = User(
            username=f"tg_{telegram_id}",
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            first_name=first_name,
            last_name=last_name,
            referral_code=code,
            referred_by_id=referred_by,
        )
        db.add(user)
        await db.flush()
        db.add(Balance(user_id=user.id))

        if referred_by:
            from app.services.settings_service import SettingsService
            reward = float(await SettingsService.get(db, "referral_reward", "2.0"))
            db.add(Referral(referrer_id=referred_by, referred_id=user.id, reward_amount=reward))
            await db.execute(
                update(Balance).where(Balance.user_id == referred_by)
                .values(amount=Balance.amount + reward, total_earned=Balance.total_earned + reward)
            )

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_balance(db: AsyncSession, user_id: int) -> Balance:
        result = await db.execute(select(Balance).where(Balance.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def add_notification(db: AsyncSession, user_id: int, title: str, body: str, ntype: str, ref_id: int = None):
        notif = Notification(user_id=user_id, title=title, body=body, type=ntype, ref_id=ref_id)
        db.add(notif)
        await db.commit()

    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def count_users(db: AsyncSession) -> int:
        result = await db.execute(select(func.count(User.id)))
        return result.scalar()
