import bdd_pytorch_service.metrics
import bdd_tensorflow_service.metrics
import bdd_log.bdd_log
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}