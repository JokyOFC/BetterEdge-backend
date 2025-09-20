from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.database import get_session
from src.db.models.core_models import Allocation

router = APIRouter()

# Refactor schemes for DB
class AllocationBase(BaseModel):
    client_id: UUID
    asset_id: UUID
    quantity: float
    avg_price: float
    ticker: str | None
    invested_amount: float
    
    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, v: str) -> str:
        return isinstance(v, str) and v.strip().upper() or ""
    

class AllocationOut(AllocationBase):
    id: UUID
    
    class config:
        orm_type = True

@router.get("/", response_model=List[AllocationOut])
async def list_allocations(session: AsyncSession = Depends(get_session)):
    
    stmt = select(Allocation)
    result = await session.execute(stmt)
    allocations = result.scalars().all()
    
    return allocations

@router.get("/{allocation_id}", response_model=AllocationOut)
async def list_allocation_by_id(allocation_id,  session: AsyncSession = Depends(get_session)):
    stmt = select(Allocation).where(Allocation.id.in_([allocation_id]))
    result = await session.execute(stmt)
    allocation = result.scalars().first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Not Found")
    
    return allocation

@router.get("/{client_id}", response_model=List[AllocationOut])
async def list_allocation_by_client_id(client_id,  session: AsyncSession = Depends(get_session)):
    stmt = select(Allocation).where(Allocation.client_id.in_([client_id]))
    result = await session.execute(stmt)
    allocation = result.scalars().first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Not Found")
    
    return allocation

@router.post("/", response_model=AllocationOut, status_code=status.HTTP_201_CREATED)
async def create_allocations(allocation:AllocationBase, session: AsyncSession = Depends(get_session)):

    if not allocation.client_id:
        raise HTTPException(status_code=status.HTTP_400, detail="Client is required.")
    
    if not allocation.asset_id:
        raise HTTPException(status_code=status.HTTP_400, detail="Asset is required.")
    
    if not isinstance(allocation.client_id, UUID):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client must be a UUID.")
    
    if not isinstance(allocation.asset_id, UUID):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset must be a UUID.")
    
    if not allocation.quantity or not allocation.avg_price or not allocation.invested_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Values must be filled.")

    if allocation.quantity < 0 or allocation.avg_price < 0 or allocation.invested_amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Values cannot be negative.")
    
    new_allocation = Allocation(
        client_id=allocation.client_id,
        asset_id=allocation.asset_id,
        quantity=allocation.quantity,
        avg_price=allocation.avg_price,
        invested_amount=allocation.invested_amount,
        ticker=allocation.ticker,
    )
    
    session.add(new_allocation)
    await session.commit()
    await session.refresh(new_allocation)
    
    return new_allocation


@router.put("/")
def update_allocations():
    return


@router.delete("/")
def delete_allocations():
    return
