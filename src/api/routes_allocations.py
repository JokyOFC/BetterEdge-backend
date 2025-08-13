from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_allocations():
    return

@router.post("/")
def create_allocations():
    return

@router.put("/")
def update_allocations():
    return

@router.delete("/")
def delete_allocations():
    return