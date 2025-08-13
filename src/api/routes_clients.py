from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_clients():
    return

@router.post("/")
def create_clients():
    return

@router.put("/")
def update_clients():
    return

@router.delete("/")
def delete_clients():
    return