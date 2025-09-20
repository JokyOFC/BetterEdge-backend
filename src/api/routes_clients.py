"""

    Refactor: change the logic to /service/ location
    
    to-do:
        - make a function to get client and dont repeat code
        -- maybe the params will be the "where" of the query

"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from src.db.database import get_session
from src.db.models.core_models import Client # Go to services

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
    
    """
    
        maybe filter the select to return just clients
        there is activated 
    
    """
    
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")

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


@router.put("/", response_model=ClientOut)
async def update_clients(
    client_id: UUID,
    client: ClientBase,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Client).where(Client.id.in_(client_id))
    result = await session.execute(stmt)
    db_client = result.scalar().first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client.model_dump(exclude_unset=True)
    for key, data in update_data.items():
        setattr(db_client, key, data)
        
    await session.commit()
    await session.refresh()
    
    return db_client


@router.delete("/")
async def delete_clients(
    client_id: UUID,
    client: ClientBase,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(client).where(client.id.in_(client_id))
    result = await session.execute(stmt)
    db_client = result.scalar().first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    """

        Think about deleting or not the client of db.
        maybe just disable the client
        and after some amount of time a task will be create
        to delete every client there is in X time without beeing activated.
    
    """
    
    return
