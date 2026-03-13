from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Boolean, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from log_service import log_event
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

from fastapi.middleware.cors import CORSMiddleware
import logging

load_dotenv()

#security 
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#BATADASE
DATABASE_USER_URL = os.getenv("DATABASE_USER_URL")
engine = create_engine(DATABASE_USER_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    firstName = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    statut = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)



Base.metadata.create_all(engine)
log_event("autentification-service", "INFO", "Table User creee dans la BDD pour les utilisateurs")

# API MODELS
class UserCreate(BaseModel):
    name: str
    firstName: str
    email: str
    statut: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    firstName: str
    email: str
    statut: str
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None




#security functions
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str)-> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    
def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Token invalide", 
                                headers={"WWW-Authenticate": "Bearer"})
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Token invalide", 
                            headers={"WWW-Authenticate": "Bearer"})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Auth Dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Utilisateur n'existe pas", 
                            headers={"WWW-Authenticate": "Bearer"})
    if token_data is None or token_data.email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Token invalide ou inexistant ou expiré", 
                            headers={"WWW-Authenticate": "Bearer"})
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Utilisateur inactif")
    return current_user



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Auth endpoints

@app.get("/")
async def root():
    return {"message": "Hello World"}

# création de compte 
@app.post("/registerUser", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        log_event("autentification-service", "WARNING", "Utilisateur deja cree")
        raise HTTPException(status_code=400,
                            detail="Email déjà utilisé")
        
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        firstName=user.firstName,
        email=user.email,
        statut="user", #user ou admin
        hashed_password=hashed_password
    )
    if user.statut == "admin" :
        new_user.statut = "admin"
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_event("autentification-service", "INFO", f"Nouvel utilisateur ajoute (id : {new_user.id})")
    return new_user

#connexion
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        log_event("autentification-service", "WARNING", "Email ou mot de passe incorrect")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Email ou mot de passe incorrect")
    if not user.is_active:
        log_event("autentification-service", "WARNING", "Utilisateur inactif")
        raise HTTPException(status_code=404, 
                            detail="Utilisateur inactif")
    
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    log_event("autentification-service", "INFO", f"connexion reussie (user id : {user.id})")
    return {"access_token": access_token, "token_type": "bearer"}


# récupérer le profil de l'utilisateur connecté
@app.get("/profil", response_model=UserResponse)
def get_profil(current_user: User = Depends(get_current_active_user)):
    return current_user

# Vérifier la validité du token et retourner les informations de l'utilisateur
@app.get("/verifyToken")
def verify_token_endpoint(current_user:User = Depends(get_current_active_user)):
    log_event("autentification-service", "INFO", "Verification du token de connection")
    return {
        "valid" : True,
        "user" : {
            "id" : current_user.id,
            "name" : current_user.name,
            "firstName" : current_user.firstName,
            "email" : current_user.email,
            "statut" : current_user.statut
        }
    }

# liste des users
@app.get("/users/", response_model=List[UserResponse])
def list_users(current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# récupérer un user par id
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int,current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user



# mettre à jour un user, depuis un compte d'un autre user connecté
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if db.query(User).filter(User.email == user.email, User.id != user_id).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    db_user.name = user.name
    db_user.firstName = user.firstName
    db_user.email = user.email
    db_user.statut = user.statut

    db.commit()
    db.refresh(db_user)
    return db_user

# supprimer un user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    
    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}



userAdmin1 = UserCreate(firstName="Georgette", name="Cy",  email="georgette.cy@coucou.com", statut="admin", password="password")
userAdmin2 = UserCreate(firstName="Victor", name="Tech",  email="victor.tech@coucou.com", statut="admin", password="password")
user1 = UserCreate(firstName="Laura", name="Carotte",  email="laura.carotte@coucou.com", statut="user", password="password")
user2 = UserCreate(firstName="George", name="Cy",  email="george.cy@coucou.com", statut="user", password="password")
user3 = UserCreate(firstName="Prince", name="Petit",  email="petit.prince@coucou.com", statut="user", password="password")

db = SessionLocal()
for user in [userAdmin1, userAdmin2, user1, user2, user3]:
    try:
        register_user(user, db)
    except HTTPException:
        pass  # user existe déjà, on ignore
db.close()

