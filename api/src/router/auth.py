from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"message": "Login successful",
            "token": "fake-jwt-token"}

@router.post("/signup")
async def register():
    return {"message": "Registration successful"}

@router.post("/logout")
async def logout():    
    return {"message": "Logout successful"}