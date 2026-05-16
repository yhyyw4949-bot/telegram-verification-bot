from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.models import Order, OrderStatus, Listing, Balance, User
from app.schemas.schemas import OrderCreate


class OrderService:

    @staticmethod
    async def create_order(db: AsyncSession, buyer_id: int, data: OrderCreate) -> Order:
        price = 0.0
        seller_id = None
        if data.listing_id:
            result = await db.execute(select(Listing).where(Listing.id == data.listing_id))
            listing = result.scalar_one_or_none()
            if listing:
                price = listing.price
                seller_id = listing.seller_id

        order = Order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            listing_id=data.listing_id,
            platform=data.platform,
            verification_type=data.verification_type,
            account_data=data.account_data,
            verification_link=data.verification_link,
            price=price,
            status=OrderStatus.pending,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_order(db: AsyncSession, order_id: int) -> Optional[Order]:
        result = await db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_orders(db: AsyncSession, user_id: int, role: str = "buyer") -> List[Order]:
        if role == "buyer":
            q = select(Order).where(Order.buyer_id == user_id).order_by(Order.created_at.desc())
        else:
            q = select(Order).where(Order.seller_id == user_id).order_by(Order.created_at.desc())
        result = await db.execute(q)
        return result.scalars().all()

    @staticmethod
    async def update_status(db: AsyncSession, order_id: int, status: OrderStatus,
                             notes: str = None, admin_id: int = None) -> Optional[Order]:
        order = await OrderService.get_order(db, order_id)
        if not order:
            return None
        order.status = status
        if notes:
            order.admin_notes = notes
        if status == OrderStatus.completed:
            order.completed_at = datetime.utcnow()
            # Pay seller
            if order.seller_id and order.price > 0:
                await db.execute(
                    update(Balance).where(Balance.user_id == order.seller_id)
                    .values(amount=Balance.amount + order.price,
                            total_earned=Balance.total_earned + order.price)
                )
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_all_orders(db: AsyncSession, status: OrderStatus = None,
                              skip: int = 0, limit: int = 50) -> List[Order]:
        q = select(Order)
        if status:
            q = q.where(Order.status == status)
        q = q.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(q)
        return result.scalars().all()

    @staticmethod
    async def count_orders(db: AsyncSession, status: OrderStatus = None) -> int:
        q = select(func.count(Order.id))
        if status:
            q = q.where(Order.status == status)
        result = await db.execute(q)
        return result.scalar()
