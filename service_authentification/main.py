from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Boolean, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta


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

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    statut = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)



Base.metadata.create_all(engine)

# API MODELS
class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    statut: str
    password: str

class UtilisateurResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    statut: str
    is_active: bool

    class Config:
        from_attributes = True

class UtilisateurLogin(BaseModel):
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
    user = db.query(Utilisateur).filter(Utilisateur.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Utilisateur n'existe pas", 
                            headers={"WWW-Authenticate": "Bearer"})
    return user

def get_current_active_user(current_user: Utilisateur = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=404, 
                            detail="Utilisateur inactif")
    return current_user



app = FastAPI()


#Auth endpoints
@app.post("/creationCompte", response_model=UtilisateurResponse)
def register_user(user: UtilisateurCreate, db: Session = Depends(get_db)):
    if db.query(Utilisateur).filter(Utilisateur.email == user.email).first():
        raise HTTPException(status_code=400,
                            detail="Email déjà utilisé")
    hashed_password = get_password_hash(user.password)
    new_user = Utilisateur(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        statut=user.statut,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Email ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(status_code=404, 
                            detail="Utilisateur inactif")
    
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/profil", response_model=UtilisateurResponse)
def get_profil(current_user: Utilisateur = Depends(get_current_active_user)):
    return current_user

@app.get("/verifyToken")
def verify_token_endpoint(current_user:Utilisateur = Depends(get_current_active_user)):
    return {
        "valid" : True,
        "utilisateur" : {
            "id" : current_user.id,
            "nom" : current_user.nom,
            "prenom" : current_user.prenom,
            "email" : current_user.email,
            "statut" : current_user.statut
        }
    }


@app.get("/utilisateurs/", response_model=List[UtilisateurResponse])
def list_users(current_user:Utilisateur = Depends(get_current_active_user), db: Session = Depends(get_db)):
    users = db.query(Utilisateur).all()
    return users


@app.get("/usutilisateurs/{user_id}", response_model=UtilisateurResponse)
def get_user(user_id: int,current_user:Utilisateur = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@app.post("/utilisateurs/", response_model=UtilisateurResponse)
def create_user(user: UtilisateurCreate, current_user:Utilisateur = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if db.query(Utilisateur).filter(Utilisateur.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    hashed_password = get_password_hash(user.password)
    new_user = Utilisateur(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        statut=user.statut,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.put("/utilisateurs/{user_id}", response_model=UtilisateurResponse)
def update_user(user_id: int, user: UtilisateurCreate, current_user:Utilisateur = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if db.query(Utilisateur).filter(Utilisateur.email == user.email, Utilisateur.id != user_id).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    db_user.nom = user.nom
    db_user.prenom = user.prenom
    db_user.email = user.email
    db_user.statut = user.statut

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/utilisateurs/{user_id}")
def delete_user(user_id: int, current_user:Utilisateur = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    
    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}


