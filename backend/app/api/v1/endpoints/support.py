from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.schemas import TicketCreate, TicketMessageCreate, TicketOut
from app.models.models import SupportTicket, TicketMessage, TicketStatus
from app.services.user_service import UserService
from typing import List

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/tickets", response_model=TicketOut, status_code=201)
async def create_ticket(data: TicketCreate, db: AsyncSession = Depends(get_db),
                         current_user=Depends(get_current_user)):
    ticket = SupportTicket(user_id=current_user.id, subject=data.subject)
    db.add(ticket)
    await db.flush()
    msg = TicketMessage(ticket_id=ticket.id, sender_id=current_user.id,
                         is_admin=False, content=data.message)
    db.add(msg)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=List[TicketOut])
async def my_tickets(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.user_id == current_user.id)
        .order_by(SupportTicket.created_at.desc())
    )
    return result.scalars().all()


@router.post("/tickets/{ticket_id}/messages")
async def reply_to_ticket(ticket_id: int, data: TicketMessageCreate,
                           db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    msg = TicketMessage(ticket_id=ticket_id, sender_id=current_user.id,
                         is_admin=current_user.is_admin, content=data.content)
    db.add(msg)
    # Notify
    notify_user = ticket.user_id if current_user.is_admin else None
    if notify_user:
        await UserService.add_notification(db, notify_user, "رد على التذكرة",
                                            f"تم الرد على تذكرتك #{ticket_id}", "support", ticket_id)
    await db.commit()
    return {"message": "Reply sent"}


# Admin - all tickets
@router.get("/admin/tickets")
async def all_tickets(status: str = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    q = select(SupportTicket)
    if status:
        q = q.where(SupportTicket.status == TicketStatus(status))
    q = q.order_by(SupportTicket.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/admin/tickets/{ticket_id}/close")
async def close_ticket(ticket_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_admin)):
    await db.execute(update(SupportTicket).where(SupportTicket.id == ticket_id)
                     .values(status=TicketStatus.closed))
    await db.commit()
    return {"message": "Ticket closed"}
