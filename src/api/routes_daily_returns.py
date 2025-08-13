from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_daily_returns():
    return

@router.post("/")
def create_daily_returns():
    return

@router.put("/")
def update_daily_returns():
    return

@router.delete("/")
def delete_daily_returns():
    return