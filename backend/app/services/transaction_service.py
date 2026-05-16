from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.models import Deposit, Withdrawal, Balance, TransactionStatus, PaymentMethod
from app.schemas.schemas import DepositCreate, WithdrawalCreate
from app.services.settings_service import SettingsService


class TransactionService:

    # ── Deposit ──────────────────────────────────────────
    @staticmethod
    async def create_deposit(db: AsyncSession, user_id: int, data: DepositCreate,
                              proof_image: str = None) -> Deposit:
        result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == data.payment_method_id))
        pm = result.scalar_one_or_none()
        dep = Deposit(
            user_id=user_id,
            amount=data.amount,
            payment_method_id=data.payment_method_id,
            payment_method_name=pm.name if pm else "Unknown",
            proof_image=proof_image,
        )
        db.add(dep)
        await db.commit()
        await db.refresh(dep)
        return dep

    @staticmethod
    async def approve_deposit(db: AsyncSession, deposit_id: int, admin_id: int) -> Optional[Deposit]:
        result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
        dep = result.scalar_one_or_none()
        if not dep or dep.status != TransactionStatus.pending:
            return None
        dep.status = TransactionStatus.approved
        dep.approved_by = admin_id
        await db.execute(
            update(Balance).where(Balance.user_id == dep.user_id)
            .values(amount=Balance.amount + dep.amount,
                    total_deposited=Balance.total_deposited + dep.amount)
        )
        await db.commit()
        await db.refresh(dep)
        return dep

    @staticmethod
    async def reject_deposit(db: AsyncSession, deposit_id: int, admin_id: int,
                              reason: str = None) -> Optional[Deposit]:
        result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
        dep = result.scalar_one_or_none()
        if not dep:
            return None
        dep.status = TransactionStatus.rejected
        dep.approved_by = admin_id
        dep.admin_notes = reason
        await db.commit()
        await db.refresh(dep)
        return dep

    @staticmethod
    async def get_pending_deposits(db: AsyncSession) -> List[Deposit]:
        result = await db.execute(
            select(Deposit).where(Deposit.status == TransactionStatus.pending)
            .order_by(Deposit.created_at.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_user_deposits(db: AsyncSession, user_id: int) -> List[Deposit]:
        result = await db.execute(
            select(Deposit).where(Deposit.user_id == user_id)
            .order_by(Deposit.created_at.desc())
        )
        return result.scalars().all()

    # ── Withdrawal ───────────────────────────────────────
    @staticmethod
    async def create_withdrawal(db: AsyncSession, user_id: int, data: WithdrawalCreate) -> Optional[Withdrawal]:
        # Check balance
        result = await db.execute(select(Balance).where(Balance.user_id == user_id))
        bal = result.scalar_one_or_none()
        min_wd = float(await SettingsService.get(db, "min_withdrawal", "5"))
        if not bal or bal.amount < data.amount or data.amount < min_wd:
            return None
        # Deduct balance
        await db.execute(
            update(Balance).where(Balance.user_id == user_id)
            .values(amount=Balance.amount - data.amount,
                    total_withdrawn=Balance.total_withdrawn + data.amount)
        )
        wd = Withdrawal(
            user_id=user_id,
            amount=data.amount,
            method=data.method,
            wallet_address=data.wallet_address,
        )
        db.add(wd)
        await db.commit()
        await db.refresh(wd)
        return wd

    @staticmethod
    async def approve_withdrawal(db: AsyncSession, wd_id: int, admin_id: int) -> Optional[Withdrawal]:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == wd_id))
        wd = result.scalar_one_or_none()
        if not wd:
            return None
        wd.status = TransactionStatus.approved
        wd.approved_by = admin_id
        await db.commit()
        await db.refresh(wd)
        return wd

    @staticmethod
    async def reject_withdrawal(db: AsyncSession, wd_id: int, admin_id: int,
                                 reason: str = None) -> Optional[Withdrawal]:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == wd_id))
        wd = result.scalar_one_or_none()
        if not wd:
            return None
        # Refund balance
        await db.execute(
            update(Balance).where(Balance.user_id == wd.user_id)
            .values(amount=Balance.amount + wd.amount,
                    total_withdrawn=Balance.total_withdrawn - wd.amount)
        )
        wd.status = TransactionStatus.rejected
        wd.approved_by = admin_id
        wd.admin_notes = reason
        await db.commit()
        await db.refresh(wd)
        return wd

    @staticmethod
    async def get_pending_withdrawals(db: AsyncSession) -> List[Withdrawal]:
        result = await db.execute(
            select(Withdrawal).where(Withdrawal.status == TransactionStatus.pending)
            .order_by(Withdrawal.created_at.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_user_withdrawals(db: AsyncSession, user_id: int) -> List[Withdrawal]:
        result = await db.execute(
            select(Withdrawal).where(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
        )
        return result.scalars().all()

    # ── Payment Methods ──────────────────────────────────
    @staticmethod
    async def get_payment_methods(db: AsyncSession) -> List[PaymentMethod]:
        result = await db.execute(
            select(PaymentMethod).where(PaymentMethod.is_active == True)
        )
        return result.scalars().all()
