from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import datetime
from app.models.models import OrderStatus, TransactionStatus, SellerStatus, TicketStatus


# ── Auth ───────────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    first_name: str
    last_name: Optional[str] = None
    referral_code: Optional[str] = None
    language: Optional[str] = "ar"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ── User ───────────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str]
    first_name: str
    last_name: Optional[str]
    telegram_id: Optional[int]
    telegram_username: Optional[str]
    is_admin: bool
    is_banned: bool
    language: str
    referral_code: str
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    language: Optional[str] = None


class BalanceOut(BaseModel):
    amount: float
    total_deposited: float
    total_withdrawn: float
    total_earned: float

    class Config:
        from_attributes = True


# ── Listing ────────────────────────────────────────────────
class ListingCreate(BaseModel):
    platform: str
    verification_type: str
    title: str
    description: Optional[str] = None
    price: float
    delivery_days: int = 1


class ListingOut(BaseModel):
    id: int
    seller_id: int
    platform: str
    verification_type: str
    title: str
    description: Optional[str]
    price: float
    delivery_days: int
    is_active: bool
    total_orders: int
    created_at: datetime
    seller: Optional[UserOut] = None

    class Config:
        from_attributes = True


# ── Order ──────────────────────────────────────────────────
class OrderCreate(BaseModel):
    listing_id: Optional[int] = None
    platform: str
    verification_type: str
    account_data: Optional[str] = None
    verification_link: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    buyer_id: int
    seller_id: Optional[int]
    platform: str
    verification_type: str
    status: OrderStatus
    price: float
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None


# ── Deposit ────────────────────────────────────────────────
class DepositCreate(BaseModel):
    amount: float
    payment_method_id: int


class DepositOut(BaseModel):
    id: int
    user_id: int
    amount: float
    payment_method_name: str
    proof_image: Optional[str]
    status: TransactionStatus
    admin_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Withdrawal ─────────────────────────────────────────────
class WithdrawalCreate(BaseModel):
    amount: float
    method: str
    wallet_address: str


class WithdrawalOut(BaseModel):
    id: int
    user_id: int
    amount: float
    method: str
    wallet_address: str
    status: TransactionStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ── Payment Method ─────────────────────────────────────────
class PaymentMethodCreate(BaseModel):
    name: str
    description: Optional[str] = None
    wallet_address: str
    instructions: Optional[str] = None


class PaymentMethodOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    wallet_address: str
    qr_code_url: Optional[str]
    instructions: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ── Review ─────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    order_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be 1-5")
        return v


class ReviewOut(BaseModel):
    id: int
    order_id: int
    reviewer_id: int
    seller_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Support ────────────────────────────────────────────────
class TicketCreate(BaseModel):
    subject: str
    message: str


class TicketMessageCreate(BaseModel):
    content: str


class TicketMessageOut(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    is_admin: bool
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketOut(BaseModel):
    id: int
    user_id: int
    subject: str
    status: TicketStatus
    created_at: datetime
    messages: List[TicketMessageOut] = []

    class Config:
        from_attributes = True


# ── Referral ───────────────────────────────────────────────
class ReferralOut(BaseModel):
    id: int
    referrer_id: int
    referred_id: int
    reward_amount: float
    reward_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notification ───────────────────────────────────────────
class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Admin ──────────────────────────────────────────────────
class AdminBalanceEdit(BaseModel):
    user_id: int
    amount: float
    operation: str   # add | subtract | set
    reason: Optional[str] = None


class AdminSettingUpdate(BaseModel):
    key: str
    value: str


class BroadcastMessage(BaseModel):
    title: str
    body: str
    target: str = "all"   # all | users | sellers


class SellerApproval(BaseModel):
    user_id: int
    status: SellerStatus
    notes: Optional[str] = None


# ── Pagination ─────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int


# ── Bot API ────────────────────────────────────────────────
class BotUserSync(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    referral_code: Optional[str] = None


class BotOrderCreate(BaseModel):
    telegram_id: int
    platform: str
    verification_type: str
    account_data: Optional[str] = None
    verification_link: Optional[str] = None


class BotDepositCreate(BaseModel):
    telegram_id: int
    amount: float
    payment_method_name: str


class BotWithdrawalCreate(BaseModel):
    telegram_id: int
    amount: float
    method: str
    wallet_address: str
