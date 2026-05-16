from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, BigInteger, String, Float, Boolean,
    DateTime, Text, ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"
    disputed = "disputed"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SellerStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


# ── Users ──────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    first_name = Column(String(100))
    last_name = Column(String(100), nullable=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    language = Column(String(10), default="ar")
    referral_code = Column(String(20), unique=True, index=True)
    referred_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    balance = relationship("Balance", back_populates="user", uselist=False)
    orders_as_buyer = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    orders_as_seller = relationship("Order", foreign_keys="Order.seller_id", back_populates="seller")
    deposits = relationship("Deposit", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")
    listings = relationship("Listing", back_populates="seller")
    tickets = relationship("SupportTicket", back_populates="user")
    referrals = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    seller_profile = relationship("SellerProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    amount = Column(Float, default=0.0)
    total_deposited = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="balance")


# ── Seller ─────────────────────────────────────────────────
class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    status = Column(SAEnum(SellerStatus), default=SellerStatus.pending)
    bio = Column(Text, nullable=True)
    total_sales = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="seller_profile")
    listings = relationship("Listing", back_populates="seller_profile")


# ── Listings ───────────────────────────────────────────────
class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    seller_profile_id = Column(Integer, ForeignKey("seller_profiles.id"))
    platform = Column(String(50))          # Binance, Bybit, etc.
    verification_type = Column(String(50)) # account, link, manual
    title = Column(String(255))
    description = Column(Text, nullable=True)
    price = Column(Float)
    delivery_days = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    total_orders = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("User", back_populates="listings")
    seller_profile = relationship("SellerProfile", back_populates="listings")
    orders = relationship("Order", back_populates="listing")


# ── Orders ─────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    platform = Column(String(50))
    verification_type = Column(String(50))
    account_data = Column(Text, nullable=True)    # encrypted
    verification_link = Column(Text, nullable=True)
    proof_images = Column(Text, nullable=True)     # JSON array of paths
    status = Column(SAEnum(OrderStatus), default=OrderStatus.pending)
    price = Column(Float, default=0.0)
    admin_notes = Column(Text, nullable=True)
    dispute_reason = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="orders_as_seller")
    listing = relationship("Listing", back_populates="orders")
    review = relationship("Review", back_populates="order", uselist=False)


# ── Transactions ───────────────────────────────────────────
class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    payment_method_name = Column(String(100))
    proof_image = Column(String(500), nullable=True)
    status = Column(SAEnum(TransactionStatus), default=TransactionStatus.pending)
    admin_notes = Column(Text, nullable=True)
    approved_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="deposits")
    payment_method = relationship("PaymentMethod")


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    method = Column(String(100))
    wallet_address = Column(String(500))
    status = Column(SAEnum(TransactionStatus), default=TransactionStatus.pending)
    admin_notes = Column(Text, nullable=True)
    approved_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="withdrawals")


# ── Payment Methods ────────────────────────────────────────
class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    wallet_address = Column(String(500))
    qr_code_url = Column(String(500), nullable=True)
    instructions = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Referrals ──────────────────────────────────────────────
class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_id = Column(Integer, ForeignKey("users.id"), unique=True)
    reward_amount = Column(Float, default=0.0)
    reward_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals")
    referred = relationship("User", foreign_keys=[referred_id])


# ── Reviews ────────────────────────────────────────────────
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)   # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="review")


# ── Support Tickets ────────────────────────────────────────
class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(255))
    status = Column(SAEnum(TicketStatus), default=TicketStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    is_admin = Column(Boolean, default=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("SupportTicket", back_populates="messages")


# ── Notifications ──────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    body = Column(Text)
    type = Column(String(50))  # order, deposit, withdrawal, referral, dispute
    is_read = Column(Boolean, default=False)
    ref_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# ── Settings ───────────────────────────────────────────────
class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Admin Logs ─────────────────────────────────────────────
class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    target_user_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
