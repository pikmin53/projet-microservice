import models.metrics
from fastapi import FastAPI
from CNNkeras import train_model
app = FastAPI()

#train_model()

@app.get("/")
async def root():
    return {"message": "Hello World"}