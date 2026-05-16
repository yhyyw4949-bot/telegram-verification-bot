from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.db.session import get_db
from app.core.security import get_current_admin
from app.schemas.schemas import (AdminBalanceEdit, AdminSettingUpdate, BroadcastMessage,
                                   SellerApproval, PaymentMethodCreate, OrderStatusUpdate)
from app.models.models import (Balance, PlatformSetting, Notification, User,
                                 SellerProfile, PaymentMethod, Order, Deposit, Withdrawal,
                                 AdminLog, OrderStatus)
from app.services.transaction_service import TransactionService
from app.services.order_service import OrderService
from app.services.settings_service import SettingsService
from app.services.user_service import UserService
from typing import List, Optional

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Dashboard Stats ────────────────────────────────────────
@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    total_users = await UserService.count_users(db)
    total_orders = await OrderService.count_orders(db)
    pending_orders = await OrderService.count_orders(db, OrderStatus.pending)
    completed_orders = await OrderService.count_orders(db, OrderStatus.completed)

    dep_result = await db.execute(
        select(func.count(Deposit.id), func.sum(Deposit.amount))
        .where(Deposit.status == "approved")
    )
    dep_count, dep_sum = dep_result.one()

    wd_result = await db.execute(
        select(func.count(Withdrawal.id), func.sum(Withdrawal.amount))
        .where(Withdrawal.status == "approved")
    )
    wd_count, wd_sum = wd_result.one()

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_deposits": dep_sum or 0,
        "deposit_count": dep_count,
        "total_withdrawals": wd_sum or 0,
        "withdrawal_count": wd_count,
    }


# ── Balance Management ─────────────────────────────────────
@router.post("/balance/edit")
async def edit_balance(data: AdminBalanceEdit, db: AsyncSession = Depends(get_db),
                        admin=Depends(get_current_admin)):
    result = await db.execute(select(Balance).where(Balance.user_id == data.user_id))
    bal = result.scalar_one_or_none()
    if not bal:
        raise HTTPException(status_code=404, detail="User balance not found")
    if data.operation == "add":
        await db.execute(update(Balance).where(Balance.user_id == data.user_id)
                         .values(amount=Balance.amount + data.amount))
    elif data.operation == "subtract":
        await db.execute(update(Balance).where(Balance.user_id == data.user_id)
                         .values(amount=Balance.amount - data.amount))
    elif data.operation == "set":
        await db.execute(update(Balance).where(Balance.user_id == data.user_id)
                         .values(amount=data.amount))
    db.add(AdminLog(admin_id=admin.id, action="balance_edit", target_user_id=data.user_id,
                    details=f"{data.operation} {data.amount}: {data.reason}"))
    await db.commit()
    return {"message": "Balance updated"}


# ── Deposits Admin ─────────────────────────────────────────
@router.get("/deposits/pending")
async def pending_deposits(db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    deposits = await TransactionService.get_pending_deposits(db)
    return [{"id": d.id, "user_id": d.user_id, "amount": d.amount,
             "payment_method_name": d.payment_method_name, "proof_image": d.proof_image,
             "created_at": d.created_at} for d in deposits]


@router.post("/deposits/{dep_id}/approve")
async def approve_deposit(dep_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    dep = await TransactionService.approve_deposit(db, dep_id, admin.id)
    if not dep:
        raise HTTPException(status_code=400, detail="Cannot approve deposit")
    await UserService.add_notification(db, dep.user_id, "إيداع مقبول",
                                        f"تم قبول إيداعك بمبلغ {dep.amount}", "deposit", dep.id)
    return {"message": "Deposit approved"}


@router.post("/deposits/{dep_id}/reject")
async def reject_deposit(dep_id: int, reason: str = "", db: AsyncSession = Depends(get_db),
                          admin=Depends(get_current_admin)):
    dep = await TransactionService.reject_deposit(db, dep_id, admin.id, reason)
    if not dep:
        raise HTTPException(status_code=404, detail="Deposit not found")
    await UserService.add_notification(db, dep.user_id, "إيداع مرفوض",
                                        f"تم رفض إيداعك: {reason}", "deposit", dep.id)
    return {"message": "Deposit rejected"}


# ── Withdrawals Admin ──────────────────────────────────────
@router.get("/withdrawals/pending")
async def pending_withdrawals(db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    wds = await TransactionService.get_pending_withdrawals(db)
    return [{"id": w.id, "user_id": w.user_id, "amount": w.amount,
             "method": w.method, "wallet_address": w.wallet_address,
             "created_at": w.created_at} for w in wds]


@router.post("/withdrawals/{wd_id}/approve")
async def approve_withdrawal(wd_id: int, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    wd = await TransactionService.approve_withdrawal(db, wd_id, admin.id)
    if not wd:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    await UserService.add_notification(db, wd.user_id, "سحب مقبول",
                                        f"تم قبول طلب سحبك بمبلغ {wd.amount}", "withdrawal", wd.id)
    return {"message": "Withdrawal approved"}


@router.post("/withdrawals/{wd_id}/reject")
async def reject_withdrawal(wd_id: int, reason: str = "", db: AsyncSession = Depends(get_db),
                             admin=Depends(get_current_admin)):
    wd = await TransactionService.reject_withdrawal(db, wd_id, admin.id, reason)
    if not wd:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    await UserService.add_notification(db, wd.user_id, "سحب مرفوض",
                                        f"تم رفض طلب سحبك: {reason}", "withdrawal", wd.id)
    return {"message": "Withdrawal rejected"}


# ── Orders Admin ───────────────────────────────────────────
@router.get("/orders")
async def all_orders(status: Optional[str] = None, skip: int = 0, limit: int = 50,
                     db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    status_enum = OrderStatus(status) if status else None
    orders = await OrderService.get_all_orders(db, status_enum, skip, limit)
    return orders


@router.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, data: OrderStatusUpdate,
                               db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    order = await OrderService.update_status(db, order_id, data.status, data.notes, admin.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await UserService.add_notification(db, order.buyer_id, "تحديث الطلب",
                                        f"تم تحديث حالة الطلب #{order_id} إلى {data.status}", "order", order_id)
    return {"message": "Order status updated"}


# ── Payment Methods ────────────────────────────────────────
@router.get("/payment-methods")
async def list_all_payment_methods(db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    result = await db.execute(select(PaymentMethod))
    return result.scalars().all()


@router.post("/payment-methods", status_code=201)
async def create_payment_method(data: PaymentMethodCreate, db: AsyncSession = Depends(get_db),
                                 _=Depends(get_current_admin)):
    pm = PaymentMethod(**data.model_dump())
    db.add(pm)
    await db.commit()
    await db.refresh(pm)
    return pm


@router.delete("/payment-methods/{pm_id}")
async def delete_payment_method(pm_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == pm_id))
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Not found")
    pm.is_active = False
    await db.commit()
    return {"message": "Payment method disabled"}


# ── Sellers ────────────────────────────────────────────────
@router.get("/sellers/pending")
async def pending_sellers(db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    result = await db.execute(select(SellerProfile).where(SellerProfile.status == "pending"))
    return result.scalars().all()


@router.post("/sellers/approve")
async def approve_seller(data: SellerApproval, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    result = await db.execute(select(SellerProfile).where(SellerProfile.user_id == data.user_id))
    sp = result.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    sp.status = data.status
    await db.commit()
    status_ar = "مقبول" if data.status == "approved" else "مرفوض"
    await UserService.add_notification(db, data.user_id, "طلب البائع",
                                        f"تم {status_ar} طلبك كبائع", "system")
    return {"message": f"Seller {data.status}"}


# ── Settings ───────────────────────────────────────────────
@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    return await SettingsService.get_all(db)


@router.put("/settings")
async def update_setting(data: AdminSettingUpdate, db: AsyncSession = Depends(get_db),
                          _=Depends(get_current_admin)):
    await SettingsService.set(db, data.key, data.value)
    return {"message": "Setting updated"}


# ── Broadcast ──────────────────────────────────────────────
@router.post("/broadcast")
async def send_broadcast(data: BroadcastMessage, db: AsyncSession = Depends(get_db),
                          admin=Depends(get_current_admin)):
    result = await db.execute(select(User).where(User.is_banned == False))
    users = result.scalars().all()
    notifs = [Notification(user_id=u.id, title=data.title, body=data.body, type="broadcast")
              for u in users]
    db.add_all(notifs)
    await db.commit()
    return {"message": f"Broadcast sent to {len(notifs)} users"}


# ── Logs ───────────────────────────────────────────────────
@router.get("/logs")
async def get_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                   _=Depends(get_current_admin)):
    result = await db.execute(
        select(AdminLog).order_by(AdminLog.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()
