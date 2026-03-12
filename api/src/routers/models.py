from fastapi import APIRouter, Depends, Request
from src.core.security import verify_token
from src.core.metrics import create_consumer, consume_metrics
from datetime import datetime


router = APIRouter()

consumer_pytorch = create_consumer("metrics_pytorch")
consumer_tensorflow = create_consumer("metrics_tensorflow")

# Récupération des métriques Kafka aprés vérification
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
                {"time": datetime.fromisoformat(metrics_pytorch["time"]).strftime("%H:%M:%S"), "pytorch": metrics_pytorch.get(key), "tensorflow": metrics_tensorflow.get(key)}
            for key in metrics_pytorch if key != "time"
        }
        if metrics is not None:
            print(f"Metrics reçues : {metrics}")
                
    return {"message": metrics, "user": value}