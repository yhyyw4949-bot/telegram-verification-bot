from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.schemas import UserOut, UserUpdate, BalanceOut, NotificationOut, ReferralOut
from app.models.models import User, Balance, Notification, Referral
from app.services.user_service import UserService
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_me(data: UserUpdate, db: AsyncSession = Depends(get_db),
                    current_user=Depends(get_current_user)):
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(current_user, field, val)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/balance", response_model=BalanceOut)
async def get_balance(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    bal = await UserService.get_balance(db, current_user.id)
    if not bal:
        raise HTTPException(status_code=404, detail="Balance not found")
    return bal


@router.get("/me/notifications", response_model=List[NotificationOut])
async def get_notifications(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.post("/me/notifications/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    await db.execute(
        update(Notification).where(Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "All notifications marked as read"}


@router.get("/me/referrals", response_model=List[ReferralOut])
async def get_referrals(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(Referral).where(Referral.referrer_id == current_user.id)
        .order_by(Referral.created_at.desc())
    )
    return result.scalars().all()


# Admin endpoints
@router.get("/", response_model=List[UserOut])
async def list_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db),
                     _=Depends(get_current_admin)):
    return await UserService.get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    user = await UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/ban")
async def ban_user(user_id: int, reason: str = "", db: AsyncSession = Depends(get_db),
                   admin=Depends(get_current_admin)):
    user = await UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_banned = True
    user.ban_reason = reason
    await db.commit()
    return {"message": "User banned"}


@router.post("/{user_id}/unban")
async def unban_user(user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    user = await UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_banned = False
    user.ban_reason = None
    await db.commit()
    return {"message": "User unbanned"}
