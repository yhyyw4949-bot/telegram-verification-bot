from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.schemas import ListingCreate, ListingOut, OrderCreate, OrderOut
from app.models.models import Listing, SellerProfile, SellerStatus
from app.services.order_service import OrderService
from app.services.user_service import UserService
from typing import List, Optional

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/listings", response_model=List[ListingOut])
async def get_listings(platform: Optional[str] = None, vtype: Optional[str] = None,
                       skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    q = select(Listing).where(Listing.is_active == True)
    if platform:
        q = q.where(Listing.platform == platform)
    if vtype:
        q = q.where(Listing.verification_type == vtype)
    q = q.order_by(Listing.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/listings", response_model=ListingOut, status_code=201)
async def create_listing(data: ListingCreate, db: AsyncSession = Depends(get_db),
                          current_user=Depends(get_current_user)):
    # Must be approved seller
    result = await db.execute(
        select(SellerProfile).where(SellerProfile.user_id == current_user.id)
    )
    sp = result.scalar_one_or_none()
    if not sp or sp.status != SellerStatus.approved:
        raise HTTPException(status_code=403, detail="Must be an approved seller to create listings")
    listing = Listing(seller_id=current_user.id, seller_profile_id=sp.id, **data.model_dump())
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return listing


@router.get("/listings/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.delete("/listings/{listing_id}")
async def delete_listing(listing_id: int, db: AsyncSession = Depends(get_db),
                          current_user=Depends(get_current_user)):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Not found")
    if listing.seller_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    listing.is_active = False
    await db.commit()
    return {"message": "Listing deactivated"}


# ── Orders ─────────────────────────────────────────────────
@router.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db),
                        current_user=Depends(get_current_user)):
    order = await OrderService.create_order(db, current_user.id, data)
    await UserService.add_notification(db, current_user.id,
                                        "طلب جديد", f"تم إنشاء الطلب #{order.id}", "order", order.id)
    return order


@router.get("/orders", response_model=List[OrderOut])
async def get_my_orders(role: str = "buyer", db: AsyncSession = Depends(get_db),
                         current_user=Depends(get_current_user)):
    return await OrderService.get_user_orders(db, current_user.id, role)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db),
                    current_user=Depends(get_current_user)):
    order = await OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.buyer_id != current_user.id and order.seller_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order


@router.post("/orders/{order_id}/dispute")
async def open_dispute(order_id: int, reason: str, db: AsyncSession = Depends(get_db),
                        current_user=Depends(get_current_user)):
    from app.models.models import OrderStatus, Order
    order = await OrderService.get_order(db, order_id)
    if not order or order.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = OrderStatus.disputed
    order.dispute_reason = reason
    await db.commit()
    return {"message": "Dispute opened"}


# ── Seller Apply ───────────────────────────────────────────
@router.post("/seller/apply")
async def apply_as_seller(bio: str = "", db: AsyncSession = Depends(get_db),
                           current_user=Depends(get_current_user)):
    result = await db.execute(select(SellerProfile).where(SellerProfile.user_id == current_user.id))
    existing = result.scalar_one_or_none()
    if existing:
        return {"message": "Application already submitted", "status": existing.status}
    sp = SellerProfile(user_id=current_user.id, bio=bio)
    db.add(sp)
    await db.commit()
    return {"message": "Seller application submitted"}
