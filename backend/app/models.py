import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, DateTime,
    ForeignKey, Text, Enum, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PurchaseStatus(str, PyEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class RaffleStatus(str, PyEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    purchases = relationship("Purchase", back_populates="user")
    raffle_entries = relationship("RaffleEntry", back_populates="user")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # in kopeks
    image_url = Column(Text, nullable=True)
    ai_prompt = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    purchases = relationship("Purchase", back_populates="certificate")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # in kopeks
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.PENDING)
    payment_id = Column(String(255), nullable=True)
    qr_code = Column(Text, nullable=True)  # base64 QR code
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="purchases")
    certificate = relationship("Certificate", back_populates="purchases")


class Raffle(Base):
    __tablename__ = "raffles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    status = Column(Enum(RaffleStatus), default=RaffleStatus.ACTIVE)
    max_entries = Column(Integer, default=100)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    certificate = relationship("Certificate")
    winner = relationship("User")
    entries = relationship("RaffleEntry", back_populates="raffle")


class RaffleEntry(Base):
    __tablename__ = "raffle_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raffle_id = Column(UUID(as_uuid=True), ForeignKey("raffles.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    raffle = relationship("Raffle", back_populates="entries")
    user = relationship("User", back_populates="raffle_entries")


class CharityOption(Base):
    __tablename__ = "charity_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    votes = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class CharityVote(Base):
    __tablename__ = "charity_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    option_id = Column(UUID(as_uuid=True), ForeignKey("charity_options.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
