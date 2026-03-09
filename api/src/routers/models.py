from fastapi import APIRouter, Depends
from src.core.security import verify_token
from fastapi import Request

router = APIRouter()

@router.get("/data")
async def get_data(request : Request):
    value = verify_token(request)
    if value is None:
        return {"message": "Invalid token"}
                
    return {"message": "Here is your data", "user": value}