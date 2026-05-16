"""
Internal API endpoints called by the Telegram bot.
Protected by API_SECRET header instead of JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import verify_bot_secret
from app.schemas.schemas import (BotUserSync, BotOrderCreate, BotDepositCreate,
                                   BotWithdrawalCreate, OrderCreate, WithdrawalCreate)
from app.services.user_service import UserService
from app.services.order_service import OrderService
from app.services.transaction_service import TransactionService
from app.models.models import PaymentMethod
from typing import Optional

router = APIRouter(prefix="/bot", tags=["Bot Internal API"])


def check_secret(x_bot_secret: str = Header(...)):
    if not verify_bot_secret(x_bot_secret):
        raise HTTPException(status_code=401, detail="Invalid bot secret")


@router.post("/sync-user")
async def sync_user(data: BotUserSync, db: AsyncSession = Depends(get_db),
                    _=Depends(check_secret)):
    user = await UserService.sync_telegram_user(
        db, data.telegram_id, data.telegram_username or "",
        data.first_name, data.last_name, data.referral_code
    )
    bal = await UserService.get_balance(db, user.id)
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "is_banned": user.is_banned,
        "is_admin": user.is_admin,
        "referral_code": user.referral_code,
        "balance": bal.amount if bal else 0,
    }


@router.get("/user/{telegram_id}")
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_db), _=Depends(check_secret)):
    user = await UserService.get_by_telegram(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bal = await UserService.get_balance(db, user.id)
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "is_banned": user.is_banned,
        "is_admin": user.is_admin,
        "referral_code": user.referral_code,
        "balance": bal.amount if bal else 0,
    }


@router.post("/orders")
async def create_bot_order(data: BotOrderCreate, db: AsyncSession = Depends(get_db),
                            _=Depends(check_secret)):
    user = await UserService.get_by_telegram(db, data.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not registered")
    order_data = OrderCreate(
        platform=data.platform,
        verification_type=data.verification_type,
        account_data=data.account_data,
        verification_link=data.verification_link,
    )
    order = await OrderService.create_order(db, user.id, order_data)
    return {"order_id": order.id, "status": order.status, "platform": order.platform}


@router.get("/orders/{telegram_id}")
async def get_bot_orders(telegram_id: int, db: AsyncSession = Depends(get_db), _=Depends(check_secret)):
    user = await UserService.get_by_telegram(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    orders = await OrderService.get_user_orders(db, user.id, "buyer")
    return [{"id": o.id, "platform": o.platform, "status": o.status,
             "created_at": o.created_at.isoformat()} for o in orders[:10]]


@router.post("/deposits")
async def create_bot_deposit(data: BotDepositCreate, db: AsyncSession = Depends(get_db),
                              _=Depends(check_secret)):
    user = await UserService.get_by_telegram(db, data.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not registered")
    # Find payment method by name
    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.name == data.payment_method_name,
                                    PaymentMethod.is_active == True)
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Payment method not found")
    from app.schemas.schemas import DepositCreate
    dep = await TransactionService.create_deposit(db, user.id,
                                                   DepositCreate(amount=data.amount,
                                                                  payment_method_id=pm.id))
    return {"deposit_id": dep.id, "amount": dep.amount, "status": dep.status,
            "wallet_address": pm.wallet_address, "instructions": pm.instructions}


@router.post("/withdrawals")
async def create_bot_withdrawal(data: BotWithdrawalCreate, db: AsyncSession = Depends(get_db),
                                 _=Depends(check_secret)):
    user = await UserService.get_by_telegram(db, data.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not registered")
    wd = await TransactionService.create_withdrawal(
        db, user.id,
        WithdrawalCreate(amount=data.amount, method=data.method, wallet_address=data.wallet_address)
    )
    if not wd:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    return {"withdrawal_id": wd.id, "amount": wd.amount, "status": wd.status}


@router.get("/payment-methods")
async def bot_payment_methods(db: AsyncSession = Depends(get_db), _=Depends(check_secret)):
    methods = await TransactionService.get_payment_methods(db)
    return [{"id": m.id, "name": m.name, "wallet_address": m.wallet_address,
             "instructions": m.instructions} for m in methods]


@router.get("/settings")
async def bot_settings(db: AsyncSession = Depends(get_db), _=Depends(check_secret)):
    from app.services.settings_service import SettingsService
    return await SettingsService.get_all(db)
