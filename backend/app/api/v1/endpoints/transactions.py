import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.schemas import DepositCreate, DepositOut, WithdrawalCreate, WithdrawalOut, PaymentMethodOut
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService
from typing import List, Optional

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/payment-methods", response_model=List[PaymentMethodOut])
async def list_payment_methods(db: AsyncSession = Depends(get_db)):
    return await TransactionService.get_payment_methods(db)


@router.post("/deposits", response_model=DepositOut, status_code=201)
async def create_deposit(
    amount: float = Form(...),
    payment_method_id: int = Form(...),
    proof: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    from app.services.settings_service import SettingsService
    min_dep = float(await SettingsService.get(db, "min_deposit", "5"))
    if amount < min_dep:
        raise HTTPException(status_code=400, detail=f"Minimum deposit is {min_dep}")

    proof_path = None
    if proof:
        os.makedirs(f"{settings.UPLOAD_DIR}/proofs", exist_ok=True)
        ext = proof.filename.rsplit(".", 1)[-1].lower()
        filename = f"dep_{current_user.id}_{int(__import__('time').time())}.{ext}"
        path = f"{settings.UPLOAD_DIR}/proofs/{filename}"
        async with aiofiles.open(path, "wb") as f:
            await f.write(await proof.read())
        proof_path = f"/uploads/proofs/{filename}"

    data = DepositCreate(amount=amount, payment_method_id=payment_method_id)
    dep = await TransactionService.create_deposit(db, current_user.id, data, proof_path)
    await UserService.add_notification(db, current_user.id,
                                        "طلب إيداع", f"تم استلام طلب الإيداع #{dep.id}", "deposit", dep.id)
    return dep


@router.get("/deposits", response_model=List[DepositOut])
async def get_my_deposits(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await TransactionService.get_user_deposits(db, current_user.id)


@router.post("/withdrawals", response_model=WithdrawalOut, status_code=201)
async def create_withdrawal(data: WithdrawalCreate, db: AsyncSession = Depends(get_db),
                             current_user=Depends(get_current_user)):
    wd = await TransactionService.create_withdrawal(db, current_user.id, data)
    if not wd:
        raise HTTPException(status_code=400, detail="Insufficient balance or amount below minimum")
    await UserService.add_notification(db, current_user.id,
                                        "طلب سحب", f"تم استلام طلب السحب #{wd.id}", "withdrawal", wd.id)
    return wd


@router.get("/withdrawals", response_model=List[WithdrawalOut])
async def get_my_withdrawals(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await TransactionService.get_user_withdrawals(db, current_user.id)
