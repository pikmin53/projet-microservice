from fastapi import FastAPI
from CNNtorch import train_model
app = FastAPI()

#train_model()

@app.get("/")
async def root():
    return {"message": "Hello World"}