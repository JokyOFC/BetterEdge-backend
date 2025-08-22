from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from src.db.database import get_session
from src.db.models.core_models import Client

router = APIRouter()


class ClientBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    tax_id: str | None = None
    advisor_id: UUID | None = None
    risk_profile: str | None = None


class ClientOut(ClientBase):
    id: UUID

    class config:
        orm_mode = True


@router.get("/", response_model=List[ClientOut])
async def list_clients(session: AsyncSession = Depends(get_session)):
    stmt = select(Client)
    result = await session.execute(stmt)
    clients = result.scalars().all()
    return clients


@router.get("/{client_id}", response_model=ClientOut)
async def list_client_by_id(client_id, session: AsyncSession = Depends(get_session)):
    stmt = select(Client).where(Client.id.in_([client_id]))
    result = await session.execute(stmt)
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Not Found")
    return client


@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_clients(
    client: ClientBase, session: AsyncSession = Depends(get_session)
):
    if not client.name:
        raise HTTPException(status_code=400, detail="Name is required")

    new_client = Client(
        name=client.name,
        email=client.email,
        phone=client.phone,
        tax_id=client.tax_id,
        advisor_id=client.advisor_id,
        risk_profile=client.risk_profile,
    )

    session.add(new_client)
    await session.commit()
    await session.refresh(new_client)
    return new_client


@router.put("/")
def update_clients():
    return


@router.delete("/")
def delete_clients():
    return
