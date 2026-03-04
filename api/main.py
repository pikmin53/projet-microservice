from fastapi import FastAPI
from src.routers.models import router as models_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(models_router, prefix="/models")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

