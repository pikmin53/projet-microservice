from fastapi import APIRouter, Depends
from src.core.security import verify_token
from fastapi import Request
from src.core.metrics import create_consumer, consume_metrics

router = APIRouter()

consumer = create_consumer()

@router.get("/data")
async def get_data(request : Request):
    value = verify_token(request)
    if value is None:
        return {"message": "Invalid token"}
    else:
        metrics = consume_metrics(consumer)
        if metrics is not None:
            print(f"Metrics reçues : {metrics}")
                
    return {"message": metrics, "user": value}