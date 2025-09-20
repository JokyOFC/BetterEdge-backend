import enum
#import yfinance as yahoo
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from src.db.database import get_session
from src.db.models.core_models import Asset
from sqlalchemy import select


router = APIRouter()

class AssetTypeEnum(str, enum.Enum):
    ACAO = "acao"
    FII = "fii"
    FUNDO = "fundo"
    RENDA_FIXA = "renda_fixa"

class AssetBase(BaseModel):
    name: str
    asset_type: AssetTypeEnum
    currency: str
    default_fee_rate: float
    has_dividend: bool
    ticker: str
    

class AssetOut(AssetBase):
    id: UUID
    
    class config:
        orm_mode = True

@router.get("/", response_model=List[AssetOut])
async def list_assets(session: AsyncSession = Depends(get_session)):
    stmt = select(Asset)
    result = await session.execute(stmt)
    assets = result.scalars().all()
    return assets

@router.get("/{asset_id}", response_model=AssetOut)
async def get_asset_by_id(asset_id, session: AsyncSession = Depends(get_session)):
    stmt = select(Asset).where(Asset.id.in_([asset_id]))
    result = await session.execute(stmt)
    asset = result.scalar().first()
    
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    
    return asset

@router.get("/ticker/{asset_ticker}", response_model=AssetOut)
async def get_asset_by_ticker(asset_ticker, session: AsyncSession = Depends(get_session)):
    stmt = select(Asset).where(Asset.ticker.in_([asset_ticker]))
    result = await session.execute(stmt)
    asset = result.scalars().first()
    
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    
    return asset

@router.post("/", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
async def create_assets(asset: AssetBase, session: AsyncSession = Depends(get_session)):
    
    """
        TODO: Verify if ticker is already registred
    """
    if not asset.ticker:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticker is required")
    
    if not asset.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
    
    if not asset.asset_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset type is required")
    
    new_asset = Asset(
        name=asset.name,
        ticker=asset.ticker,
        asset_type=asset.asset_type,
        currency=asset.currency,
        default_fee_rate=asset.default_fee_rate,
        has_dividend=asset.has_dividend
    )
    
    session.add(new_asset)
    await session.commit()
    await session.refresh(new_asset)
    
    return new_asset


@router.put("/")
def update_assets():
    return


@router.delete("/")
def delete_assets():
    return
