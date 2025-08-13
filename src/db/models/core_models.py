import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Numeric, Enum, ForeignKey, Boolean, Date, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AssetTypeEnum(str, enum.Enum):
    ACAO = "acao"
    FII = "fii"
    FUNDO = "fundo"
    RENDA_FIXA = "renda_fixa"
    MOEDA = "moeda"
    ETF = "etf"
    OUTRO = "outro"

class Client(Base):
    __tablename__ = 'clients'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    tax_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    advisor_id = Column(UUID(as_uuid=True), nullable=True)
    risk_profile = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    asset_type = Column(Enum(AssetTypeEnum), nullable=False)
    currency = Column(String(3), default='BRL')
    default_fee_rate = Column(Numeric(10,6), default=0.0)
    has_dividend = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Allocation(Base):
    __tablename__ = 'allocations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Numeric(28,8), nullable=False, default=0)
    avg_price = Column(Numeric(18,6), nullable=False, default=0)
    invested_amount = Column(Numeric(18,2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('client_id', 'asset_id', name='uq_client_asset'),
    )

class DailyReturn(Base):
    __tablename__ = 'daily_returns'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(18,6))
    high = Column(Numeric(18,6))
    low = Column(Numeric(18,6))
    close = Column(Numeric(18,6), nullable=False)
    volume = Column(Numeric(28,2))
    adjusted_close = Column(Numeric(18,6))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('asset_id', 'date', name='uq_asset_date'),
    )
