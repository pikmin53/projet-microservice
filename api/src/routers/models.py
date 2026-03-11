from fastapi import APIRouter, Depends, Request
from src.core.security import verify_token
from src.core.metrics import create_consumer, consume_metrics

router = APIRouter()

consumer_pytorch = create_consumer("metrics_pytorch")
consumer_tensorflow = create_consumer("metrics_tensorflow")

@router.get("/data")
async def get_data(request : Request):
    value = verify_token(request)
    if value is None:
        return {"message": "Invalid token"}
    else:
        metrics_pytorch = consume_metrics(consumer_pytorch)
        metrics_tensorflow = consume_metrics(consumer_tensorflow)
        if metrics_pytorch is None or metrics_tensorflow is None:
            return {"message": {}, "user": value}
        metrics = {
            key: 
                {"time": metrics_pytorch["time"], "pytorch": metrics_pytorch[key], "tensorflow": metrics_tensorflow[key]}
            for key in metrics_pytorch if key != "time"
        }
        if metrics is not None:
            print(f"Metrics reçues : {metrics}")
                
    return {"message": metrics, "user": value}