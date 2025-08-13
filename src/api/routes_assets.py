from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_assets():
    return

@router.post("/")
def create_assets():
    return

@router.put("/")
def update_assets():
    return

@router.delete("/")
def delete_assets():
    return